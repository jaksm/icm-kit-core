---
trust_tier: unverified
---

# An old repo, a folder, a disk

Inventory with `find` (and `git log --stat` if it is a repo), never by opening files: names, sizes,
dates. Before anything else, search for secrets twice and report the hits as paths only: with the
pattern from `core/scripts/leak-check.sh --pattern`, which knows token formats, and by name and
keyword (`grep -rliE 'passwor|login|kennwort|secret|token' .`), because a plain password in a note
matches no token format. A file flagged either way is not opened. `.env` files, key files and browser profiles are never opened.

A repo's history may hold what its files no longer do; that is a reason to report, not to dig.
Large binaries stay where they are: a record in the ICM points at them.
