[English](README.md) · **Português (Brasil)**

# jsonld-graph-check

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) ![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)

`jsonld-graph-check` é um validador gratuito, de código aberto, para a
integridade de um `@graph` de JSON-LD: `@id` ausente ou duplicado,
referência que aponta para um nó que não existe no grafo, e nó isolado
sem nenhuma ligação com o resto da estrutura. Confere também a paridade
mínima de `FAQPage` com as perguntas que ela deveria enumerar. Roda
localmente.

## Sumário

- [Contexto](#contexto)
- [O que a ferramenta verifica](#o-que-a-ferramenta-verifica)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Perguntas frequentes](#perguntas-frequentes)
- [Limitações](#limitações)
- [Método e origem](#método-e-origem)
- [Como contribuir](#como-contribuir)
- [Autor](#autor)
- [Licença](#licença)

## Contexto

Um validador de sintaxe JSON confirma que o arquivo é um JSON válido.
Isso não garante que o grafo faz sentido como estrutura de entidades
ligadas. Um `@graph` bem montado (`Organization`, `Person`, `WebPage`,
`Article`, `FAQPage`, todos ligados por `@id`) ajuda um sistema de IA a
confirmar quem é a entidade por trás da página. Um `@graph` fragmentado
(nós soltos sem `isPartOf` ou `mainEntity` amarrando tudo à entidade
principal) costuma aparecer no Rich Results Test do Google como cards
desconectados, e essa falta de amarração enfraquece a confirmação de
entidade.

## O que a ferramenta verifica

1. **`@id` ausente ou duplicado.** Todo nó do grafo precisa de um
   identificador único.
2. **Referência solta.** Toda referência pura (`{"@id": "..."}`) precisa
   apontar para um nó que existe no mesmo grafo, ou para um domínio
   externo explicitamente permitido (`schema.org` e `doi.org` por
   padrão).
3. **Nó isolado.** Nó sem nenhuma referência de entrada nem de saída fica
   marcado como aviso.
4. **Paridade de `FAQPage`.** Se existir um nó `FAQPage`, confere que
   `hasPart` ou `mainEntity` apontam para nós `Question` que realmente
   existem no grafo.

## Requisitos

Python 3.9 ou mais recente. Só biblioteca padrão, sem dependência
externa.

## Instalação

```bash
git clone https://github.com/LucasFerrazSEO/jsonld-graph-check.git
cd jsonld-graph-check
```

## Uso

**1. Rode contra um arquivo HTML renderizado.** A ferramenta extrai
automaticamente os blocos `<script type="application/ld+json">`.

```bash
python jsonld_graph_check.py pagina.html
```

**2. Ou aponte direto para um `.json`** com o JSON-LD, se já tiver
exportado.

```bash
python jsonld_graph_check.py schema.json
```

**3. Passe vários arquivos de uma vez**, por exemplo todas as páginas de
um diretório.

```bash
python jsonld_graph_check.py *.html
```

**4. Leia o relatório.** Exemplo de saída real, de um grafo com problema
proposital:

```
=== jsonld-graph-check: 1 grafo(s) em 1 arquivo(s) ===
ERROS 2 | AVISOS 2

  ERRO  [schema.json] referência solta (aponta para nó inexistente): https://exemplo.com/#q1
  ERRO  [schema.json] FAQPage https://exemplo.com/#faq aponta pergunta inexistente: https://exemplo.com/#q1
  AVISO [schema.json] nó possivelmente isolado: https://exemplo.com/#faq (tipo FAQPage)
  AVISO [schema.json] nó possivelmente isolado: https://exemplo.com/#orfao (tipo Thing)
```

ERRO é problema estrutural real; AVISO pode ser proposital (uma entidade
autocontida, por exemplo).

**5. Libere domínios externos extras**, se seu grafo referencia entidade
fora do seu próprio site. A opção pode ser repetida.

```bash
python jsonld_graph_check.py pagina.html --permitir-externo https://minhaempresa.com
```

**6. Use em CI/CD** antes de todo deploy. O código de saída é 1 se houver
qualquer erro (aviso não conta).

## Perguntas frequentes

**jsonld-graph-check é realmente grátis?**
Sim, código aberto sob licença MIT.

**Isso substitui o Rich Results Test do Google?**
Não. Esta ferramenta valida estrutura e integridade referencial do grafo.
Não valida contra as regras de rich results de um tipo específico
(`Product`, `Article`...) nem contra o vocabulário oficial do schema.org.
Use os dois: esta ferramenta antes do deploy, o Rich Results Test depois.

**Preciso de internet para usar?**
Não. A ferramenta só lê o arquivo local; nenhum dado sai da sua máquina.

**Funciona com Microdata ou RDFa, além de JSON-LD?**
Não, só JSON-LD, que é o formato que o Google recomenda hoje.

## Limitações

Valida estrutura e integridade referencial do grafo, não a validade
contra um tipo específico de schema.org nem o vocabulário oficial. Um "nó
isolado" é aviso, não erro: algumas entidades (`DefinedTerm` de glossário
externo, por exemplo) são legitimamente autocontidas.

## Método e origem

Generalização de um script de validação usado internamente no
[lucasferraz.com](https://lucasferraz.com) para conferir o `@graph` de
Pessoa e entidade antes de todo deploy de schema, sem a lógica específica
de página-casa e `@id` fixos daquele site.

## Como contribuir

Relatos de erro e sugestões são bem-vindos pelas [Issues do GitHub](https://github.com/LucasFerrazSEO/jsonld-graph-check/issues).

## Autor

[Lucas Ferraz](https://lucasferraz.com) é especialista em SEO, criação de sites e Generative Engine Optimization e fundador da [Lucas Ferraz SEO](https://lucasferrazseo.com).

## Licença

MIT. Veja o arquivo [LICENSE](LICENSE).
