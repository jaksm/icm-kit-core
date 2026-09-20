# 06 Remote

A private repo on a host, reached only through encryption.

## Detect

```bash
git remote get-url origin | grep -c '^gcrypt::'      # 1
git ls-remote origin | grep -c refs/heads/main       # 1
```

## Ask

Which hosting account, and a name for the repo. A name that does not describe the content is better
than one that does: the name is the one thing the host can read.

## Do

```bash
gh auth status || gh auth login --web --git-protocol ssh      # browser login: theirs
gh repo create <name> --private                                # on their word
git remote add origin "gcrypt::git@github.com:<account>/<name>.git"
F=$(git config user.signingkey)
git config remote.origin.gcrypt-participants "$F"
git config remote.origin.gcrypt-signingkey "$F"
git config remote.origin.gcrypt-publish-participants true
git push -u origin main
```

`.githooks/pre-push` refuses any push that is not to the `gcrypt::` remote or not to `main`; that is
what keeps a plain `git push` from ever uploading the ICM unencrypted. Show them the refusal once,
on purpose, so they have seen it: add a plain remote, try to push, remove it.

Two rules to say out loud, because gcrypt pushes behave like a forced push:

- `git pull --rebase origin main` before every push. It is the only place you can see that the remote moved.
- Only `main`. Branches and pull requests do not exist on an encrypted repo.

## Checkpoint

Creating the repo, and the browser login.

## Writes

Git config only. Record host, account and repo name in `domains/system/output/connectors-and-routines.md`.

## Proof

Both Detect commands print `1`, and the host shows no file names:
`gh api repos/<account>/<name>/contents --jq '.[].name'` lists only long hexadecimal names.
