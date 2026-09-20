---
name: core-update
description: Update the core/ folder of an ICM repo to a newer icm-kit-core release without losing what the owner changed. Use when the owner asks to update the system, when a migration guide is mentioned, or when core.lock is older than the latest release.
---

# Update core

`core/` in this repo is a copy of a release of icm-kit-core. `core.lock` records the version and a
hash of every file the owner was given. Everything else in the repo is the owner's and an update
never touches it.

## Steps

1. Get the release: clone or pull `icm-kit-core` into a temporary folder outside this repo.
2. `<release>/install.sh <this repo> --status`. It prints the installed and the available version
   and every file in `core/` whose hash no longer matches the lock.
3. Read every `MIGRATIONS/<from>-<to>.md` between the two versions, oldest first. A migration says
   what moved, what config key changed, and what the owner's repo must change outside `core/`.
4. For each locally edited file, read the diff against the new release and decide with the owner:
   the edit belongs in config (move it to `config/`), upstream (say so, it is a contribution), or it
   is obsolete. Do not decide silently; show the file and the reason.
5. `<release>/install.sh <this repo>` (or `--force` once step 4 is settled; edited files are kept
   beside the new ones as `<file>.local`).
6. Apply the steps each migration lists for outside `core/`: hook paths, config keys, renamed scripts.
7. Run the repo's pre-commit hook and build every artifact once. Report what changed in the
   owner's language, and delete the `.local` files that were resolved.

## Never

- Edit `core.lock` by hand, or copy single files out of a release.
- Put the owner's words, names or paths into `core/`. What is personal lives in `config/`.
