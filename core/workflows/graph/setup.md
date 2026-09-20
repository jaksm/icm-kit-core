# Setting up the graph

Part of core; nothing to install.

## Ask

Nothing required. If the ICM is not in English, write the labels in the owner's language.

## Writes

`_config/graph.json`, all keys optional: any label from the `LABELS` dictionary in
`scripts/build-graph-page.py`, plus `nested` (folders whose children are the groups, usually
`["domains"]`), `archive` (prefix of the groups drawn in grey) and `out` (default `pages/graph.html`).

To change how the page looks, copy `template/graph-template.html` to
`_config/overrides/core/workflows/graph/template/` and change the copy.

## First run and proof

`python3 core/workflows/graph/scripts/build-graph-page.py --check` prints node, edge and orphan
counts and writes the page. The page holds the whole text of the ICM: it is git ignored, and it is
published only as a private page.
