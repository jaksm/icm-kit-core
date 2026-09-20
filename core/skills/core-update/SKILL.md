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

0. **Get the release, outside the ICM.** `git clone --depth 1 --branch v<version> https://github.com/jaksm/icm-kit-core <temporary folder>`;
   releases are tags, and `CHANGELOG.md` lists them. Without `--branch` you get the latest. Read
   `CHANGELOG.md` from the installed version up: when a release in between says something is
   `required` outside `core/`, update **one release at a time**, finishing every step for each. When it
   says `required only if ...`, test the condition it names (usually a `grep` for an old path in the
   owner's files); if it does not hold, go on.
   Before anything else, commit once as things are: if the hook already fails, that is the owner's
   to fix first, and it must not be mistaken for something the update broke.
1. `<release>/install.sh <this ICM> --status`. It prints the installed and the available version,
   every file in `core/` whose hash no longer matches the lock, and `.local` copies left by an earlier update.
2. Read the migrations between the two versions, oldest first. A migration says what moved, what
   key in `_config/` changed, and what the ICM must change outside `core/`.
3. **Checkpoint.** For each locally edited file, find **the owner's edit alone**: get the installed
   version too (`git clone --branch v<installed>`), and diff *that* against the owner's file. A diff
   against the new release mixes their lines with everything upstream changed. A workflow's files
   are at `catalog/<name>/` in a release and at `core/workflows/<name>/` in the ICM. Also check that
   the edit **works at all** where it is (a line after an `exit`, a rule no file triggers): an edit
   that never ran is carried forward as kept unless someone looks, so tell the owner. Show it and decide
   together, never silently, where it goes:
   - a page template or an adapter hook: a changed copy in `_config/overrides/<same path>`, made from
     the **new** release's file plus their lines. `_config/README.md` lists what is read from there.
     An adapter hook's override takes effect only when the adapter's setup script is generated
     again and installed; say so, it is the owner's step;
   - a rule of their own in a check: its own script in `_config/checks/`, which the pre-commit hook
     runs after the core checks. Copying a core script into overrides would freeze it;
   - a value: a key in `_config/` or an environment variable in their hook, if the file reads one;
   - useful to everyone: an issue or a pull request on icm-kit-core, and until it lands, one of the above;
   - obsolete: dropped, on their word.
   **Overrides they already have** are edits too: diff each file under `_config/overrides/` against
   the new release's file it was copied from, and carry upstream's changes into it, or the owner
   stays on an old template without knowing. Every override is listed in
   `domains/system/output/connectors-and-routines.md`.
4. Move every edit to its new home **first**, prove it takes effect there (right after the install,
   when only the new code reads that home), and only then run
   `<release>/install.sh <this ICM> --force`. With edits present a plain install refuses; `--force`
   keeps each edited file beside the new one as `<file>.local` and prints which.
5. Apply what each migration lists for outside `core/`: hook paths, keys in `_config/`, renamed
   scripts. Search the owner's files for every old path the migration names: `grep -rn "<old path>" --exclude-dir=core .`
6. **Resolve every `.local`**: it is resolved when its content lives in one of the homes above or the
   owner dropped it; then delete it. `.local` files are ignored by git, so one that is left is invisible.
7. Audit: `git config core.hooksPath` answers `.githooks` (set it if not, or the hook never ran);
   commit and watch the hook pass; build every page once: the graph, each installed workflow that has
   a `build-*-page.py`, and whatever `domains/system/output/pages.md` lists.

## Outputs

- `core/` and `core.lock` at the new version, no `.local` file left unresolved.
- A short report to the owner, in their language, of what changed and what they had to decide.

## Never

- Edit `core.lock` by hand, or copy single files out of a release **into `core/`**. (A copy into
  `_config/overrides/` is how an override is made.)
- Put the owner's words, names or paths into `core/`. What is personal lives in `_config/`.
