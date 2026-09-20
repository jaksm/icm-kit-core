# icm-ui

Web components for pages an AI agent builds for one person: a daily feed, a calculator, a chart of
where the money goes. Built with [Lit](https://lit.dev), shipped as one inline file, because that is
what an artifact sandbox accepts.

Part of [icm-kit](https://github.com/jaksm/icm-kit), usable on its own.

## Why it looks the way it does

- **One self-contained page.** An artifact's CSP blocks scripts it does not control, and a page that
  fetches at runtime breaks offline. `build.py` inlines the stylesheet and the bundled module into
  your template, so the published page is a single HTML file.
- **No chart library.** SVG draws, CSS holds state, JavaScript only computes over input. A local HTML
  file previewed in a desktop app is often a static snapshot where scripts never run, and a chart
  that needs a library then shows nothing, silently.
- **Light DOM.** Every element renders without a shadow root, so one global stylesheet serves all
  instances and page-level fixes keep working.
- **Two surfaces.** Every component reads `--c-*` variables; the surface class (`on-paper`,
  `on-photo`) decides what they mean. The same component sits on a card or over an image.
- **Schema and code cannot drift.** `schema.json` lists every component with when to use it, and
  `build.py --check` fails if a component exists in one and not the other. The schema is what an
  agent reads before it writes a page.

## Components

| Element | Shows |
| --- | --- |
| `icm-metric` | the number a card is built around, with unit and label |
| `icm-delta` | how far a number sits from something else |
| `icm-gauge` | how far along, with a tick at the target |
| `icm-series` | the shape over time, as a line or bars |
| `icm-deadline` | days to a date, counted from today, so a page does not go stale |
| `icm-tags` | state pills, only for state that changes what you do |
| `icm-list`, `icm-facts`, `icm-quote`, `icm-next` | lists, compared pairs, exact wording, the one next move |
| `icm-action` | one thing a card can do: open a link or call a connector, with a fix per error code |
| `icm-choice`, `icm-slider`, `icm-input`, `icm-confirm` | the page asking a question |

## Primitives

Plain classes (and three small elements) that compose with each other and with the components. A component never
carries an outer margin: the container spaces it, which is what lets anything sit anywhere.

| Kind | Primitives |
| --- | --- |
| layout | `icm-page`, `icm-stack`, `icm-cluster`, `icm-grid`, `icm-divider` |
| text | `icm-title`, `icm-heading`, `icm-subheading`, `icm-text`, `icm-caption`, `icm-eyebrow`, `icm-mono`, `icm-num`, `icm-mark` |
| surfaces | `icm-card` (`is-pressable`, `is-marked`, `is-plain`), `icm-sheet`, `icm-shade` |
| rows | `icm-row` (`is-current`), `icm-table` |
| meters | `icm-bar`, `icm-segments`, `icm-dot`, `icm-badge` |
| controls | `<icm-button>`, `<icm-link>`, `<icm-icon>`, `icm-option`, `icm-field`, `icm-question`, `icm-tabs` |

Tokens live in `tokens/`: one design system, light and dark, no host-matched variant. A page loads the fonts itself
(`build.FONTS_LINK`). `python3 build.py --docs` builds `docs/index.html`, which shows every primitive and component
live with its markup, the existing pages assembled from them, and five pages that could be built next.

## Use

Put two slots in your template and run it through `inline()`:

```html
<style>/*ICM-CSS*/</style>
<body class="on-paper">
  <icm-deadline date="2026-12-01" label="tax return"></icm-deadline>
  <script type="module">/*ICM-JS*/</script>
```

```python
import sys; sys.path.insert(0, "path/to/icm-ui")
from build import inline
open("page.html", "w").write(inline(open("template.html").read()))
```

From a bundler (Astro, Vite) the same two files are a package, no Python involved:

```js
import "icm-ui/css";   // dist/icm.css: tokens, primitives, components
import "icm-ui";       // dist/icm.js: registers every <icm-*> element
```

`dist/` is written by `python3 build.py --bundle`; `--check` fails when `dist/icm.css` is stale.

## Another language

The library speaks English. Put a `labels.json` **beside** the library folder (not inside it) and
`inline()` injects it; see `primitives/labels.js` for the keys. Plurals go through
`Intl.PluralRules`, so the file holds only the word forms:

```json
{"locale": "de", "today": "heute", "dueIn": "in {n} {days}", "days": {"one": "Tag", "other": "Tagen"}}
```

`actions.json` is the catalog of what `icm-action` may do. It names connectors, so a repo usually
keeps its own copy.

## Design language

Calm brutal: cold paper, blue-black ink, ultramarine for what can be acted on, one yellow marker for what is current,
Archivo and IBM Plex Mono, 1.5px borders, 8px corners, a hard shadow only on what can be pressed. `docs/` is the
concept and the documentation in one page; `DESIGN.md` is the written record and the status. `build.py --check`
fails when schema and code drift, or when a text token drops under WCAG AA on any ground.

## Develop

```bash
python3 build.py --bundle    # rebuild dist/icm.js (needs npx esbuild, only here, never at page build)
python3 build.py --check     # tokens, bundle, schema and code parity
node labels-check.mjs        # plural selection
```

`vendor/lit.js` is Lit 3 bundled to one import-free file; `vendor/README.md` has the recipe.

MIT.
