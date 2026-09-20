# Changelog

One entry per release, newest first. Every entry ends with **Outside core**: `nothing`, or `required`, which
means the migration note lists work in your own files and `core-update` must stop at that release before going on.

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
