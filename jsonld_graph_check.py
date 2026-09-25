#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jsonld-graph-check — valida a integridade de um `@graph` de JSON-LD: `@id`
ausente ou duplicado, referência que aponta para um nó que não existe no
grafo, e nó isolado (sem nenhuma ligação de entrada ou saída com o resto do
grafo). Também confere a paridade estrutural mínima de `FAQPage`.

O QUE FAZ
    Lê um ou mais arquivos HTML (extrai os blocos
    `<script type="application/ld+json">`) ou arquivos `.json` com o
    JSON-LD direto, e roda quatro checagens sobre cada `@graph` encontrado:

    1. todo nó tem `@id`;
    2. nenhum `@id` se repete dentro do mesmo grafo;
    3. toda referência pura (`{"@id": "..."}`) aponta para um nó existente
       no grafo, ou para um domínio externo explicitamente permitido;
    4. nó sem nenhuma referência de entrada nem de saída fica marcado como
       possivelmente isolado (não é erro automático — pode ser proposital);
    5. se houver `FAQPage`, confere que `hasPart` ou `mainEntity` apontam
       para nós `Question` existentes no grafo.

    Um `@graph` fragmentado (nós soltos sem ligação com a entidade principal
    da página) costuma aparecer no Rich Results Test do Google como cards
    desconectados — este script pega esse problema antes do deploy.

USO
    python jsonld_graph_check.py pagina1.html pagina2.html
    python jsonld_graph_check.py schema.json
    python jsonld_graph_check.py *.html --permitir-externo https://schema.org --permitir-externo https://doi.org

LIMITAÇÕES
    Valida estrutura e integridade referencial, não valida contra as regras
    de rich results de um tipo específico (`Product`, `Article`...) nem
    contra o vocabulário oficial do schema.org — para isso, use o Rich
    Results Test do Google depois. Um "nó isolado" é um aviso, não um erro:
    algumas entidades (`DefinedTerm`, glossário externo) são legitimamente
    autocontidas.

Autor: Lucas Ferraz (lucasferraz.com) — dependência zero, só biblioteca padrão.
Licença: MIT.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field

BLOCO_JSONLD = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)


@dataclass
class Relatorio:
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def erro(self, msg: str) -> None:
        self.erros.append(msg)

    def aviso(self, msg: str) -> None:
        self.avisos.append(msg)


def extrai_blocos(conteudo: str, eh_json: bool) -> list[dict]:
    if eh_json:
        return [json.loads(conteudo)]
    blocos = []
    for m in BLOCO_JSONLD.findall(conteudo):
        try:
            blocos.append(json.loads(m))
        except json.JSONDecodeError:
            continue
    return blocos


def para_grafo(doc: dict) -> list[dict]:
    if "@graph" in doc:
        return doc["@graph"]
    return [doc]


def coleta_referencias(no: object, refs: set[str]) -> None:
    if isinstance(no, dict):
        if set(no.keys()) == {"@id"}:
            refs.add(no["@id"])
            return
        for valor in no.values():
            coleta_referencias(valor, refs)
    elif isinstance(no, list):
        for item in no:
            coleta_referencias(item, refs)


def checa_grafo(grafo: list[dict], rotulo: str, externos_ok: tuple[str, ...],
                 relatorio: Relatorio) -> None:
    ids: dict[str, dict] = {}
    for no in grafo:
        tipo = no.get("@type", "?")
        oid = no.get("@id")
        if not oid:
            relatorio.erro(f"[{rotulo}] nó sem @id (tipo {tipo})")
            continue
        if oid in ids:
            relatorio.erro(f"[{rotulo}] @id repetido: {oid}")
            continue
        ids[oid] = no

    referencias: set[str] = set()
    coleta_referencias(grafo, referencias)
    for ref in sorted(referencias):
        if ref in ids:
            continue
        if any(ref.startswith(prefixo) for prefixo in externos_ok):
            continue
        relatorio.erro(f"[{rotulo}] referência solta (aponta para nó inexistente): {ref}")

    # nós de entrada/saída para checar isolamento
    referenciados_por_outros: set[str] = set()
    for oid, no in ids.items():
        refs_deste_no: set[str] = set()
        coleta_referencias(no, refs_deste_no)
        refs_deste_no.discard(oid)
        for r in refs_deste_no:
            if r in ids:
                referenciados_por_outros.add(r)

    for oid, no in ids.items():
        refs_deste_no: set[str] = set()
        coleta_referencias(no, refs_deste_no)
        refs_deste_no.discard(oid)
        tem_saida = bool(refs_deste_no & set(ids))
        tem_entrada = oid in referenciados_por_outros
        if not tem_saida and not tem_entrada:
            relatorio.aviso(f"[{rotulo}] nó possivelmente isolado: {oid} (tipo {no.get('@type', '?')})")

    for oid, no in ids.items():
        if no.get("@type") != "FAQPage":
            continue
        partes = no.get("hasPart") or no.get("mainEntity") or []
        if isinstance(partes, dict):
            partes = [partes]
        alvos = []
        for p in partes:
            if isinstance(p, dict) and "@id" in p:
                alvos.append(p["@id"])
        if not alvos:
            relatorio.aviso(f"[{rotulo}] FAQPage {oid} sem hasPart/mainEntity apontando perguntas")
            continue
        for alvo in alvos:
            alvo_no = ids.get(alvo)
            if alvo_no is None:
                relatorio.erro(f"[{rotulo}] FAQPage {oid} aponta pergunta inexistente: {alvo}")
            elif alvo_no.get("@type") != "Question":
                relatorio.aviso(f"[{rotulo}] FAQPage {oid} aponta nó que não é Question: {alvo}")

    if not any(rotulo in e for e in relatorio.erros):
        print(f"  ok  {rotulo}: {len(ids)} nó(s), {len(referencias)} referência(s)")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Valida a integridade de um @graph de JSON-LD (HTML ou JSON)."
    )
    ap.add_argument("arquivos", nargs="+", help="arquivo(s) .html ou .json")
    ap.add_argument("--permitir-externo", action="append", default=[],
                     help="prefixo de URL externa aceito como referência válida "
                          "(ex.: https://schema.org). Pode repetir.")
    args = ap.parse_args()

    externos_padrao = ("https://schema.org", "http://schema.org", "https://doi.org")
    externos_ok = externos_padrao + tuple(args.permitir_externo)

    relatorio = Relatorio()
    total_grafos = 0
    for caminho in args.arquivos:
        eh_json = caminho.lower().endswith(".json")
        try:
            with open(caminho, encoding="utf-8") as fh:
                conteudo = fh.read()
        except OSError as exc:
            relatorio.erro(f"não consegui ler {caminho}: {exc}")
            continue

        try:
            docs = extrai_blocos(conteudo, eh_json)
        except json.JSONDecodeError as exc:
            relatorio.erro(f"{caminho}: JSON inválido ({exc})")
            continue

        if not docs:
            relatorio.aviso(f"{caminho}: nenhum bloco JSON-LD encontrado")
            continue

        for i, doc in enumerate(docs):
            rotulo = caminho if len(docs) == 1 else f"{caminho}#{i}"
            checa_grafo(para_grafo(doc), rotulo, externos_ok, relatorio)
            total_grafos += 1

    print(f"\n=== jsonld-graph-check: {total_grafos} grafo(s) em {len(args.arquivos)} arquivo(s) ===")
    print(f"ERROS {len(relatorio.erros)} | AVISOS {len(relatorio.avisos)}\n")
    for e in relatorio.erros:
        print("  ERRO  " + e)
    for a in relatorio.avisos:
        print("  AVISO " + a)

    sys.exit(1 if relatorio.erros else 0)


if __name__ == "__main__":
    main()
