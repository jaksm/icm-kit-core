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

Primitives: `icm-icon`, `icm-link`, `icm-button`. Tokens live in `tokens/`; the default palette is
matched to the Claude app so an artifact reads as part of it. Change `tokens/colors.css` to restyle.

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

`DESIGN.md` is the working record: what exists, where each page leaves the language, and what is still
to be decided. `python3 build.py --workbench` builds one page with every token and component on both
surfaces, under every palette and theme.

## Develop

```bash
python3 build.py --bundle    # rebuild dist/icm.js (needs npx esbuild, only here, never at page build)
python3 build.py --check     # tokens, bundle, schema and code parity
node labels-check.mjs        # plural selection
```

`vendor/lit.js` is Lit 3 bundled to one import-free file; `vendor/README.md` has the recipe.

MIT.
