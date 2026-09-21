# Changelog

One entry per release, newest first. Every entry ends with **Outside core**: `nothing`, or `required`, which
means the migration note lists work in your own files and `core-update` must stop at that release before going on.

## 0.7.3
`import` has a recipe for an ICM the owner already has: it moves by area with one decision table, not in groups of five; identity files are merged, old skills and hooks are not brought.
**Outside core**: nothing. [MIGRATIONS/0.7.2-0.7.3.md](MIGRATIONS/0.7.2-0.7.3.md)

## 0.7.2
`core/ui` is icm-ui 0.6.2: the mark (what is current, chosen, changed) is the accent washed into the card instead of pale blue, with the scheme's ink on it and the accent as the rim of a marked control. Text on the mark is 10.6:1 in light and 8.2:1 in dark.
**Outside core**: nothing. [MIGRATIONS/0.7.1-0.7.2.md](MIGRATIONS/0.7.1-0.7.2.md)

## 0.7.1
`core/ui` is icm-ui 0.6.1: a marked option, tab, row or card is a fill with the glass rim (no ink bar, no ink border), and focus rings are the accent color.
**Outside core**: nothing. [MIGRATIONS/0.7.0-0.7.1.md](MIGRATIONS/0.7.0-0.7.1.md)

## 0.7.0
One theme. `core/ui` is icm-ui 0.6.0: Aquarium, Pearl, Manrope (glass: translucent cards over a soft depth, a faint white rim, 20px corners, no shadow), baked into the library. A page switches light and dark and nothing else. `_config/theme.json`, `_config/themes/` and `ICM_THEME` are no longer read; the theme editor page (added after 0.6.0, never in a release) is gone, and the builder lives in a separate library.
**Outside core**: nothing; a `_config/theme.json` you may have is ignored and can be deleted. [MIGRATIONS/0.6.0-0.7.0.md](MIGRATIONS/0.6.0-0.7.0.md)

## 0.6.0
New look, one design system: `core/ui` is icm-ui 0.3.2 ("calm brutal": cold paper, ink, ultramarine for what can be acted on, one yellow marker, Archivo and IBM Plex Mono, hard edges, no host-matched variant). The feed, expenses and graph templates are rebuilt from the library's primitives and write no color, gradient or font of their own; category and node colors are the `--cat` tokens. Every builder has `--demo` (the page from mock data shipped beside the template, into `previews/`), and `scripts/build-previews.py` builds all of them with an index. `icm-action` with `confirm` is confirmed by holding. `RELEASING.md` step 3 now includes the previews.
**Outside core**: required only if you keep a changed copy of a page template in `_config/overrides/`. [MIGRATIONS/0.5.2-0.6.0.md](MIGRATIONS/0.5.2-0.6.0.md)

## 0.5.2
New: icm-ui 0.2.0 in `core/ui`: an opt-in palette (`data-palette="archive"`) and the `--mark` token. Pages look the same unless they ask for the palette. A new ICM no longer inherits the kit's landing page, which moved to its own repo.
**Outside core**: nothing. [MIGRATIONS/0.5.1-0.5.2.md](MIGRATIONS/0.5.1-0.5.2.md)

## 0.5.1
New: tests for `install.sh` (`tests/run.sh`), release tags, `RELEASING.md`. Fixed: `--remove` deleted a workflow before checking for the owner's edits in it; it is now refused without `--force`, and with it the folder is kept as `<name>.local`. `core-update` says how to get a release and was run against a real conflict; setup step 14 was run to the end.
**Outside core**: nothing. [MIGRATIONS/0.5.0-0.5.1.md](MIGRATIONS/0.5.0-0.5.1.md)

## 0.5.0
New: the `feed` workflow (funnel of signals, media, the page of rows and cards), `page-host.js` in the adapter so no page names a harness, optional line limits in `style-check.sh`.
Moved: `check-feed.py` from the `sources` workflow to `core/scripts/`. **Outside core**: required only if your own files name the old path. [MIGRATIONS/0.4.0-0.5.0.md](MIGRATIONS/0.4.0-0.5.0.md)

## 0.4.0
New: setup step 12, the `import` and `expenses` workflows; the statement parser is a recipe, not code. `remind.sh` verified on macOS.
**Outside core**: nothing. [MIGRATIONS/0.3.0-0.4.0.md](MIGRATIONS/0.3.0-0.4.0.md)

## 0.3.0
New: recipes with trust tiers (`core/RECIPES.md`), the `sources` and `morning-review` workflows, setup steps 09, 10 and 13, recipes for Windows, Linux, Android.
**Outside core**: required, skip `core` in your link check or every commit is refused. [MIGRATIONS/0.2.0-0.3.0.md](MIGRATIONS/0.2.0-0.3.0.md)

## 0.2.0
New: the setup skill with adoption of an existing ICM, the catalog with `--add` and `--remove`, the recovery USB, overrides in `_config/overrides/`.
**Outside core**: see the note. [MIGRATIONS/0.1.0-0.2.0.md](MIGRATIONS/0.1.0-0.2.0.md)

## 0.1.0
The commit checks, the Claude adapter, the vendored component library, the graph, `install.sh` and `core.lock`. For an ICM that existed before the kit: [MIGRATIONS/pre-kit-0.1.0.md](MIGRATIONS/pre-kit-0.1.0.md)
