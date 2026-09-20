# Design language: where it stands

One language for two kinds of page: the pages an agent builds for one person (feed, expenses, graph,
anything new) and the kit's own landing page. Both read the same tokens from `tokens/`. This file is
the working record of the refinement: what exists, where pages break the language, and what is
still to be decided. Open the workbench while reading it:

```bash
python3 build.py --workbench && python3 -m http.server 8912 --directory workbench
```

## What exists

| Layer | Where | State |
| --- | --- | --- |
| Color, type, layout, motion tokens | `tokens/*.css` | in use by every page |
| Surfaces: `on-paper`, `on-photo` | `tokens/surface.css` | a component reads only `--c-*`, the surface decides |
| Palettes | `colors.css` (host-matched, the default), `palettes/archive.css` (opt-in, `data-palette="archive"`) | **archive is a draft**: the landing page's first pass, as tokens |
| Light and dark | `prefers-color-scheme`, or `data-theme` | both palettes have both |
| Components | 15 components, 3 primitives, `schema.json` | each shown on both surfaces on the workbench |
| `--mark` | `colors.css` | new: the highlighter for what is being read or followed right now; only the landing page uses it yet |

## The pages, and where each one leaves the language

| Page | Source | Uses tokens | Leaves them |
| --- | --- | --- | --- |
| Feed | icm-kit-core `catalog/feed/template/feed-template.html` | fonts, `--over*`, `--paper`, `--ink*`, `--accent`, radius, motion | 19 literal colors: the dark ground `#1a1917`, every scrim stop (`rgba(20,19,17,…)` instead of `--scrim-ink`), segment and dot whites; sizes and spacing are all literal |
| Expenses | icm-kit-core `catalog/expenses/` | tokens for text and lines | category inks are 12 literal hexes in `build-expenses-page.py`; state colors `good/near/bad` are its own |
| Graph | icm-kit-core `core/workflows/graph/template/` | tokens for chrome | 5 literal colors; node colors computed in script |
| Landing | icm-kit-site `index.src.html` | all colors, type and radius from tokens (archive palette) | light only (`data-theme="light"`), two literals (`#F6EFD6` for the "it does not" panel, `#E6ECF2` on the prompt); layout, scale and spacing are its own |

## To decide, roughly in this order

1. **One palette or two.** The default is matched to the host app so a page reads as part of it; the
   archive palette gives the kit a face of its own. Either pages stay host-matched and only the site
   is archive, or archive becomes the default and host-matched the option. Everything below depends on this.
2. **Type.** Host palette: serif for what is read, sans for what is operated. Archive: one grotesque
   plus a mono for paths. Decide per palette, or one rule for both. Web fonts cost a request and a
   published page's policy must allow the font host.
3. **A scale.** There are no size or space tokens: every page invents its own numbers. Candidate:
   a type scale and a 4 px space scale as tokens, used first on the landing page and the feed.
4. **The dark ground of the feed** as tokens (`--ground`, the scrim from `--scrim-ink`), so a palette can move it.
5. **Data colors.** A categorical ramp and the three state colors as tokens, shared by expenses, the
   graph and `icm-series`.
6. **`--mark`.** Where else the highlighter belongs: the current row of the feed, the routed row in the graph.
7. **The landing page's dark mode**, once 1 is decided.
8. Motion: what moves, per the rule in `tokens/motion.css`; the landing page's "follow the agent" is the one orchestrated moment there.

## Rules that already hold, and stay

Light DOM, one global stylesheet. No chart library: SVG draws, CSS holds state. A component never
reads a color directly, only `--c-*`. Every string on screen comes from labels. A page works with
scripts off as far as it can, and respects `prefers-reduced-motion`. `build.py --check` fails when
schema and code drift.
