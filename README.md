# jsonld-graph-check — validador grátis e de código aberto de schema JSON-LD

`jsonld-graph-check` é um validador gratuito, de código aberto, para a
integridade de um `@graph` de JSON-LD: `@id` ausente ou duplicado,
referência que aponta para um nó que não existe no grafo, e nó isolado sem
nenhuma ligação com o resto da estrutura. Confere também a paridade mínima
de `FAQPage` com as perguntas que ela deveria enumerar.

## Por que validar o grafo, não só a sintaxe

Um validador de sintaxe JSON confirma que o arquivo é um JSON válido. Isso
não garante que o grafo faz sentido como estrutura de entidades ligadas. Um
`@graph` bem montado (`Organization`, `Person`, `WebPage`, `Article`,
`FAQPage` todos ligados por `@id`) ajuda um sistema de IA a confirmar quem
é a entidade por trás da página. Um `@graph` fragmentado — nós soltos sem
`isPartOf`/`mainEntity` amarrando tudo à entidade principal — costuma
aparecer no Rich Results Test do Google como cards desconectados, e essa
falta de amarração enfraquece a confirmação de entidade.

## O que a ferramenta verifica

1. **`@id` ausente ou duplicado** — todo nó do grafo precisa de um
   identificador único.
2. **Referência solta** — toda referência pura (`{"@id": "..."}`) precisa
   apontar para um nó que existe no mesmo grafo, ou para um domínio
   externo explicitamente permitido (`schema.org` e `doi.org` por padrão).
3. **Nó isolado** — nó sem nenhuma referência de entrada nem de saída fica
   marcado como aviso.
4. **Paridade de `FAQPage`** — se existir um nó `FAQPage`, confere que
   `hasPart` ou `mainEntity` apontam para nós `Question` que realmente
   existem no grafo.

## Instalação

Só biblioteca padrão do Python (3.9 ou mais recente). Sem dependência
externa.

```bash
git clone https://github.com/lucasferrazseo/jsonld-graph-check.git
cd jsonld-graph-check
```

## Como usar, passo a passo

**1. Rode contra um arquivo HTML renderizado.** A ferramenta extrai
automaticamente os blocos `<script type="application/ld+json">`:

```bash
python jsonld_graph_check.py pagina.html
```

**2. Ou aponte direto para um `.json`** com o JSON-LD, se já tiver
exportado:

```bash
python jsonld_graph_check.py schema.json
```

**3. Passe vários arquivos de uma vez**, por exemplo todas as páginas de
um diretório:

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
fora do seu próprio site:

```bash
python jsonld_graph_check.py pagina.html --permitir-externo https://minhaempresa.com
```

**6. Use em CI/CD** antes de todo deploy: código de saída 1 se houver
qualquer erro (não conta aviso).

## Perguntas frequentes

**jsonld-graph-check é realmente grátis?**
Sim, código aberto sob licença MIT.

**Isso substitui o Rich Results Test do Google?**
Não. Este valida estrutura e integridade referencial do grafo — não valida
contra as regras de rich results de um tipo específico (`Product`,
`Article`...) nem contra o vocabulário oficial do schema.org. Use os dois:
esta ferramenta antes do deploy, o Rich Results Test depois.

**Preciso de internet para usar?**
Não. A ferramenta só lê o arquivo local; nenhum dado sai da sua máquina.

**Funciona com Microdata ou RDFa, além de JSON-LD?**
Não, só JSON-LD, que é o formato que o Google recomenda hoje.

## Limitações

Valida estrutura e integridade referencial do grafo, não a validade contra
um tipo específico de schema.org nem o vocabulário oficial. Um "nó
isolado" é aviso, não erro: algumas entidades (`DefinedTerm` de glossário
externo, por exemplo) são legitimamente autocontidas.

## Método e origem

Generalização de um script de validação usado internamente no
[lucasferraz.com](https://lucasferraz.com) para conferir o `@graph` de
Pessoa/entidade antes de todo deploy de schema, sem a lógica específica de
página-casa e `@id` fixos daquele site.

## Autor

[Lucas Ferraz](https://lucasferraz.com) — especialista em SEO, criação de
sites e SEO para IA, fundador da [Lucas Ferraz SEO](https://lucasferrazseo.com).

## Licença

MIT — ver [LICENSE](LICENSE).
