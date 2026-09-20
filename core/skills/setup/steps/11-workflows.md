# 11 Workflows (optional)

Offer what the ICM can do beyond holding knowledge. Nothing is installed unless they want it.

## Detect

`grep '^module ' core.lock` lists what is installed from the catalog. Already installed and set up:
nothing to do for it.

## Ask

Get a release of `icm-kit-core` into a temporary folder outside the ICM and read `catalog/index.md`.
Offer only rows whose folder exists in that release. For each: what they would get, in one sentence
in their manner, and what it needs (a connector, a routine, a sample file). Recommend at most two
to start with. A system grown one piece at a time is understood; one installed in an afternoon is not.

The graph of the ICM is part of core. Build it now and show it:

```bash
python3 core/workflows/graph/scripts/build-graph-page.py
```

then open or publish `pages/graph.html` the way the adapter says. It is private by nature: the page holds the whole text of the ICM.

## Do

For each chosen workflow:

```bash
<release>/install.sh . --add <name>
```

then read `core/workflows/<name>/setup.md` and follow it. It says what to ask, which keys to write
in `_config/`, how to run it once, and its own proof. If the workflow needs something only this
owner has (their bank's statement format, their sources), its `recipes/` tell you how to build that
part in **their** `skills/` folder. Never in `core/`.

## Checkpoint

The choice, and anything a workflow's `setup.md` marks as one.

## Writes

`core.lock` (by `install.sh`), keys in `_config/`, a row in `skills/CONTEXT.md` for anything built
from a recipe, a row in `domains/system/output/pages.md` for every page that was published.

## Proof

`pages/graph.html` exists, and each installed workflow's own proof passed.
