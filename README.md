**English** · [Português (Brasil)](README.pt-BR.md)

# jsonld-graph-check

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) ![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)

`jsonld-graph-check` is a free, open source validator for the integrity
of a JSON-LD `@graph`: missing or duplicate `@id`, references that point
to a node that does not exist in the graph, and isolated nodes with no
link to the rest of the structure. It also checks the minimal parity of
`FAQPage` with the questions it should list. It runs locally, and the
tool prints its report in Brazilian Portuguese.

## Contents

- [Background](#background)
- [What it checks](#what-it-checks)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [FAQ](#faq)
- [Limitations](#limitations)
- [Methodology](#methodology)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

## Background

A JSON syntax validator confirms that the file is valid JSON. That does
not mean the graph makes sense as a structure of linked entities. A
well-built `@graph` (`Organization`, `Person`, `WebPage`, `Article`,
`FAQPage`, all linked by `@id`) helps an AI system confirm who the entity
behind the page is. A fragmented `@graph` (loose nodes with no
`isPartOf` or `mainEntity` tying them to the main entity) often shows up
in Google's Rich Results Test as disconnected cards, and that lack of
linking weakens entity confirmation.

## What it checks

1. **Missing or duplicate `@id`.** Every node in the graph needs a unique
   identifier.
2. **Dangling references.** Every bare reference (`{"@id": "..."}`) must
   point to a node that exists in the same graph, or to an explicitly
   allowed external domain (`schema.org` and `doi.org` by default).
3. **Isolated nodes.** A node with no incoming and no outgoing reference
   is flagged as a warning.
4. **`FAQPage` parity.** If there is a `FAQPage` node, it checks that
   `hasPart` or `mainEntity` point to `Question` nodes that actually exist
   in the graph.

## Requirements

Python 3.9 or newer. Standard library only, no external dependencies.

## Installation

```bash
git clone https://github.com/LucasFerrazSEO/jsonld-graph-check.git
cd jsonld-graph-check
```

## Usage

**1. Run it on a rendered HTML file.** The tool extracts the
`<script type="application/ld+json">` blocks automatically.

```bash
python jsonld_graph_check.py pagina.html
```

**2. Or point it straight at a `.json` file** with the JSON-LD, if you
already exported it.

```bash
python jsonld_graph_check.py schema.json
```

**3. Pass several files at once**, for example every page in a folder.

```bash
python jsonld_graph_check.py *.html
```

**4. Read the report.** A real output example, from a graph with a
deliberate problem:

```
=== jsonld-graph-check: 1 grafo(s) em 1 arquivo(s) ===
ERROS 2 | AVISOS 2

  ERRO  [schema.json] referência solta (aponta para nó inexistente): https://exemplo.com/#q1
  ERRO  [schema.json] FAQPage https://exemplo.com/#faq aponta pergunta inexistente: https://exemplo.com/#q1
  AVISO [schema.json] nó possivelmente isolado: https://exemplo.com/#faq (tipo FAQPage)
  AVISO [schema.json] nó possivelmente isolado: https://exemplo.com/#orfao (tipo Thing)
```

ERRO (error) is a real structural problem. AVISO (warning) may be
intentional (a self-contained entity, for example).

**5. Allow extra external domains** if your graph references an entity
outside your own site. The flag can be repeated.

```bash
python jsonld_graph_check.py pagina.html --permitir-externo https://minhaempresa.com
```

**6. Use it in CI/CD** before every deploy. The exit code is 1 when there
is any error (warnings do not count).

## FAQ

**Is jsonld-graph-check really free?**
Yes. It is open source under the MIT license.

**Does it replace Google's Rich Results Test?**
No. This tool validates the structure and referential integrity of the
graph. It does not validate against the rich result rules of a specific
type (`Product`, `Article`...) or against the official schema.org
vocabulary. Use both: this tool before the deploy, the Rich Results Test
after it.

**Do I need an internet connection?**
No. The tool only reads the local file. No data leaves your machine.

**Does it work with Microdata or RDFa, besides JSON-LD?**
No, only JSON-LD, which is the format Google recommends today.

## Limitations

It validates the structure and referential integrity of the graph, not
validity against a specific schema.org type or the official vocabulary.
An "isolated node" is a warning, not an error: some entities (a
`DefinedTerm` from an external glossary, for example) are legitimately
self-contained.

## Methodology

This is a generalization of a validation script used internally on
[lucasferraz.com](https://lucasferraz.com) to check the Person and entity
`@graph` before every schema deploy, without the logic specific to that
site's home page and fixed `@id` values.

## Contributing

Bug reports and suggestions are welcome through [GitHub Issues](https://github.com/LucasFerrazSEO/jsonld-graph-check/issues).

## Author

[Lucas Ferraz](https://lucasferraz.com) is an SEO, website development and Generative Engine Optimization specialist and the founder of [Lucas Ferraz SEO](https://lucasferrazseo.com).

## License

MIT. See [LICENSE](LICENSE).
