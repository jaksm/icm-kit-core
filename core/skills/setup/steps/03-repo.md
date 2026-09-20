# 03 Repo

The ICM folder exists, is its own git repo, and runs the checks on every commit.

## Detect

```bash
git rev-parse --show-toplevel && test -f core.lock && git config core.hooksPath
```
All three succeed, and the last prints `.githooks`.

## Ask

Where the ICM should live and what to call the folder. Suggest `~/<firstname>-icm`.

## Do

```bash
git clone https://github.com/jaksm/icm-kit <folder> && cd <folder>
rm -rf .git && git init -b main && git config core.hooksPath .githooks
# what belongs to the kit and not to an ICM: its landing page, its docs, its notes for contributors
rm -rf docs CONTRIBUTING.md README.md setup-prompt.md
git config user.name "<their name>" && git config user.email "<their email>"
git add -A && git commit -m "Start"
```

The template's history is dropped on purpose: this is their repo from its first commit.
If the template was already cloned by the setup prompt, only do what is missing.

## Writes

Nothing outside git.

## Proof

`git log --oneline | wc -l` prints `1` or more, and the commit output ended with
`link-check: 0 dangling links` and `style-check: 0 findings`.
