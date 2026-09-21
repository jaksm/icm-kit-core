# Releasing icm-kit-core

1. Raise `VERSION`. Write `MIGRATIONS/<from>-<to>.md` (even when nothing moved: say so) and the entry in `CHANGELOG.md`.
2. `tests/run.sh` must pass. It also fails when the version has no changelog entry or no migration note.
3. `./sync-ui.sh` if icm-ui changed. Every script's own `--check`, and `scripts/build-previews.py`: open each page it builds, in light and dark (`?theme=dark`).
4. The maintainer's scan of the three repos: 0 findings.
5. Commit, `git tag v<version>`, `git push --follow-tags`. The tests install old releases from these tags, so a release without a tag cannot be tested against later.
6. `install.sh` into the template (icm-kit), commit and push it.

A release is never edited after its tag. A fix is the next patch version.
