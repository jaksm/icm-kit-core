---
name: core-update
description: Update the core/ folder of an ICM to a newer icm-kit-core release without losing what the owner changed. Use when the owner asks to update the system, when a migration guide is mentioned, or when core.lock is older than the latest release.
---

# Update core

`core/` in an ICM is a copy of a release of icm-kit-core. `core.lock` records the version and a
hash of every file the owner was given. Everything else in the ICM is the owner's and an update
never touches it.

## Inputs

- `core.lock` at the root: the installed version and what was given.
- A release of `icm-kit-core`, cloned or pulled into a temporary folder outside the ICM.
- Every `MIGRATIONS/<from>-<to>.md` between the two versions.

## Process

1. `<release>/install.sh <this ICM> --status`. It prints the installed and the available version
   and every file in `core/` whose hash no longer matches the lock.
2. Read the migrations between the two versions, oldest first. A migration says what moved, what
   key in `_config/` changed, and what the ICM must change outside `core/`.
3. **Checkpoint.** For each locally edited file, show the owner the diff against the new release
   and decide together: the edit belongs in `_config/`, upstream (it is a contribution), or it is
   obsolete. Never decide this silently.
4. `<release>/install.sh <this ICM>`, or `--force` once step 3 is settled; edited files are kept
   beside the new ones as `<file>.local`.
5. Apply what each migration lists for outside `core/`: hook paths, keys in `_config/`, renamed scripts.
6. Audit: run the pre-commit hook and build every page once.

## Outputs

- `core/` and `core.lock` at the new version, no `.local` file left unresolved.
- A short report to the owner, in their language, of what changed and what they had to decide.

## Never

- Edit `core.lock` by hand, or copy single files out of a release.
- Put the owner's words, names or paths into `core/`. What is personal lives in `_config/`.
