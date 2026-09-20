# pre-kit to 0.1.0

The worked example: moving an existing ICM, which grew its own checks, adapter, component library
and graph builder inside `skills/` and `scripts/`, onto a vendored `core/`.

## What changed and why

The parts that are the same for everyone left the repo and came back as `core/`, so they can be
updated without touching anything personal. What was personal inside those parts moved to `_config/`.

## Moved or renamed

| Old path | New path |
| --- | --- |
| `scripts/leak-check.sh`, `link-check.sh`, `style-check.sh` | `core/scripts/` |
| the harness skill with `hooks/` and `scripts/` | `core/adapters/claude/` |
| the component library folder inside the design skill | `core/ui/` |
| the graph builder and its template | `core/workflows/graph/` |
| `labels.json` beside the library | `_config/labels.json` |
| the graph config beside the builder | `_config/graph.json`, with a new `out` key holding the old output path |
| `actions.json` inside the library | `_config/actions.json` (the library now ships an English default) |

## Outside core/

1. `install.sh <repo>`, then delete the old copies listed above.
2. `.githooks/pre-push` is a symlink: repoint it to `../core/adapters/claude/hooks/pre-push`.
3. `.githooks/pre-commit`: call `./core/scripts/*.sh`. The old style profile is gone; set
   `STYLE_TEMPLATES` to the pathspec of your templates and `STYLE_NO_CYRILLIC=1` if you need it,
   and add `core/` to `STYLE_CHECK_SKIP`. Build the graph with
   `core/workflows/graph/scripts/build-graph-page.py`.
4. Every page builder that imported the library's `build.py`: change the folder to `core/ui`
   under the repo root. A builder that read `actions.json` from the library reads `_config/actions.json`.
5. Replace the old paths in the instruction file and in records; `link-check.sh` lists the ones you missed.
6. Regenerate the cloud environment with `core/adapters/claude/scripts/make-cloud-setup.sh`: the
   setup script embeds the hooks, and it was generated from the old path.

## Verify

```bash
./core/scripts/link-check.sh            # 0 dangling links
git commit                               # the hook runs all three checks from core/
python3 core/workflows/graph/scripts/build-graph-page.py --check   # same node and edge counts as before, plus core's own records
# build every page once; each must produce a page
```

Found while doing it: `install.sh` refused a git worktree (there `.git` is a file), and skipping
every dot folder dropped a third of the graph, because an imported archive kept records in nested
dot folders. Both are fixed in 0.1.0.
