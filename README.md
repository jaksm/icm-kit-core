# icm-kit-core

The part of an ICM that is the same for everyone: checks, the harness adapter, the component
library, core workflows and the skills that run the system. It is copied into a repo as `core/`
and updated as a whole.

An ICM is a personal knowledge base an AI agent works in: a git repo of markdown files with a
router at the top. No vector database, no server, nothing to keep running. Start from the template,
[icm-kit](https://github.com/jaksm/icm-kit); this repo is what the template vendors.

## What is inside

| Folder | What it holds |
| --- | --- |
| `core/scripts/` | Three commit checks with no dependencies: `leak-check.sh` (secrets), `link-check.sh` (pointers to files that do not exist), `style-check.sh` (rules a machine can enforce). Repo specifics come in through environment variables set in the repo's own hook. |
| `core/adapters/` | Everything that depends on one harness. `claude/` today; the contract for the next one is `adapters/README.md`. |
| `core/ui/` | A vendored release of [icm-ui](https://github.com/jaksm/icm-ui), the web components artifacts are built from. |
| `core/workflows/graph/` | Builds a searchable graph page of the whole repo. |
| `core/skills/` | Skills that operate the system itself, starting with `core-update`. |

## Install and update

```bash
./install.sh <repo>            # copies core/ and writes core.lock
./install.sh <repo> --status   # what the owner edited since, and which version is installed
```

`core.lock` holds the version and a hash per file, so an update can tell a local edit from an old
release. Updates are run by the agent through the `core-update` skill, which reads `MIGRATIONS/`
between the two versions and adapts the owner's customizations instead of overwriting them.

## The rule that keeps it shareable

Nothing personal lives in `core/`. What is yours goes in `config/` at the repo root
(`config/labels.json`, `config/graph.json`) or in your own hook, and `core/` reads it from there.
Nothing outside `core/adapters/` names a harness, a vendor or a model.

## Lineage

ICM is the Interpretable Context Methodology by Jake Van Clief: folder structure as the
orchestration layer, one agent reading the right files at the right moment.
[RinDig/Interpretable-Context-Methodology](https://github.com/RinDig/Interpretable-Context-Methodology), MIT.
icm-kit takes that idea from a workflow workspace to a knowledge base about one person's life and work.

MIT.
