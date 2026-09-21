# Design language: glass, one theme

One design system and one theme for every page an agent builds for its owner: Aquarium, palette Pearl, type Manrope,
baked into `build.py` (`THEME`). A page switches only light and dark. The theme builder and the other themes moved to
`aura-ui` (0.6.0); nothing here reads a theme from config. The concept and the documentation are one page:

```bash
python3 build.py --docs && python3 -m http.server 8912 --directory .   # then /docs/  (?theme=dark, ?only=components, ?audit=1 for a visual pass)
```

## Decided

| Axis | Decision |
| --- | --- |
| Palettes | One: Pearl, light and dark. `themes/aquarium.json` holds the values; the token files are the fallback underneath. |
| Color | Warm paper and ink over a soft two-color depth (`--page-bg`), a rust accent only for what can be acted on or followed, the marker for current, chosen, changed. Every text token passes WCAG AA on every ground; `build.py --check` enforces it. |
| The marker | Never decoration and never alone: a marked thing also gets an ink bar. |
| Type | Manrope variable, JetBrains Mono only for paths, file contents and captions of figures. Six sizes 13 to 28, nothing under 13, body 16. Headings balance, prose is `pretty`, changing numbers are tabular. |
| Shape | 1px translucent edges, 20px corners, cards are glass (`--card-fill` plus `backdrop-filter`). No shadow anywhere: no glow, no halo. Pressing moves the thing 2px down. |
| Edges | Two strengths, both white with low alpha so they read as the rim of glass: `--edge` for what is read (a card, a table, a frame), `--edge-strong` for what is pressed or typed into. Focus is a 2px accent ring. Rows live in `icm-card is-list` (no padding, clipped), so a marked row meets the card's corners. |
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
