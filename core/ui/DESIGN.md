# Design language: calm brutal

One design system for every page an agent builds for its owner. It shares a brand with the kit's site
(`icm-kit-site/DESIGN.md`, loud) and none of its volume: these pages are used daily on a phone. The concept and the
documentation are one page, built from the real components:

```bash
python3 build.py --docs && python3 -m http.server 8912 --directory .   # then /docs/  (?theme=dark, ?only=components, ?audit=1 for a visual pass)
```

## Decided

| Axis | Decision |
| --- | --- |
| Palettes | One. The host-matched look and the `archive` draft are gone (0.3.0). |
| Color | Paper `#EEF1F4`, ink `#16202B` at three strengths, ultramarine `#2A3FE0` only for what can be acted on or followed, marker `#F2CB4E` for current, chosen, changed. Every text token passes WCAG AA on every ground; `build.py --check` enforces it. |
| The marker | Never decoration and never alone: yellow on paper is a weak contrast, so a marked thing also gets an ink bar. |
| Type | Archivo variable and IBM Plex Mono (only for paths, file contents, captions of figures). Six sizes 13 to 28, nothing under 13, body 16. Headings balance, prose is `pretty`, changing numbers are tabular. |
| Shape | 1.5px ink borders, 8px corners, a 3px hard shadow only on what can be pressed; pressing moves the thing into its shadow. No blur, no gradient. No hard shadows over a photo. |
| Edges | Two strengths, both ink with alpha so nested edges never fight: `--edge` for what is read (a card, a table, a frame), `--edge-strong` for what is pressed or typed into. A strong edge plus the hard shadow means "you can act". In the dark theme the shadow is the strong edge's color, so it reads as thickness, not glow. Rows live in `icm-card is-list` (no padding, clipped), so a marked row meets the card's corners. |
| Accent | `--accent` as text and line, `--accent-fill` as a filled shape (primary button, bars); the fill keeps white text in both themes. A loud number is loud by size, not by color. |
| Surfaces | `on-paper` and `on-photo`; a component reads only `--c-*`. Text over a photo always sits on the scrim. |
| Composition | Primitives are plain classes (layout, text, surfaces, rows, meters, controls). Components are fixed compositions of them, render nothing without data, and carry no outer margin: the container spaces them. |
| Motion | How often decides how much: constant input is instant, daily is subtle, a rare success may celebrate (the burst). Transform and opacity only, exits faster than entrances, transitions where input can interrupt. A hover never changes the metrics of text; content never fades in; everything is still under reduced motion. |
| Confirming | What changes something outside is confirmed by holding (the marker fills the button left to right), never by a red warning. Keyboard and reduced motion get a neutral second press. |

## Proposed, not settled

The dark theme's values, the space scale `--s-1…--s-9`, state and category colors (`tokens/data.css`), the burst.

## Not done

The feed, expenses and graph templates in icm-kit-core still carry their own markup and literal colors (feed 19,
expenses 12, graph 5); the recipes they move to are in part 2 of the docs. Core is not released with 0.3.0 until they
move, because the new default changes every page. The gaps found while assembling five future pages are listed under
each in part 4 of the docs. Fonts come from Google Fonts.

## Rules that already hold, and stay

Light DOM, one global stylesheet. No chart library: SVG draws, CSS holds state. A component never
reads a color directly, only `--c-*`. Every string on screen comes from labels. A page works with
scripts off as far as it can, and respects `prefers-reduced-motion`. `build.py --check` fails when
schema and code drift.
