---
name: icm-adapter-claude
type: Skill
title: ICM system on Claude, encrypted repo usable from phone and cloud
description: How an encrypted ICM (git + git-remote-gcrypt on GitHub) is opened in Claude Code cloud sessions, so the owner can read and write it from the Claude mobile app with the laptop off. Key generator, setup script, hooks that sync after every reply, conflict handling, revocation. Written for an admin who sets it up for non-technical users; contains no personal data.
status: active
trust_tier: verified
tags: [icm, adapter, claude-code, cloud, gcrypt, gpg, hooks]
---

# ICM system on Claude

Public, reusable. An ICM here is a personal knowledge base: a git repo of markdown files with a
`CLAUDE.md` router, pushed to GitHub through `git-remote-gcrypt`, so GitHub only ever holds an
encrypted blob. This skill makes that repo usable from Claude Code cloud sessions (claude.ai/code,
including the Claude mobile app), without an always-on computer.

Who does what: an **admin** (technical) runs the setup once per user. The **user** (not technical)
only picks an environment and a repo when starting a session on the phone. Everything that can go
wrong after setup is handled by hooks or by one sentence Claude says to the user.

## How it works

```
phone -> claude.ai cloud session
  setup script   (once per environment, cached ~7 days, no env vars): installs gnupg + git-remote-gcrypt,
                 writes public keys, ownertrust, hooks, ~/.claude/settings.json
  SessionStart   (every session, has env vars): imports ICM_GPG_KEY, renames plain GitHub remote to
                 github-raw (push disabled), adds the gcrypt remote as icm, unlocks main
  Stop           (after every reply): asks Claude to commit, rebases on icm/main, pushes HEAD:main
repo .githooks/pre-push (every machine): refuses unencrypted pushes and any branch but main
```

Facts this design rests on, checked 2026-09-17 against the Claude Code docs and in live sessions:

- Cloud routines and sessions clone from GitHub, so an encrypted repo needs its key inside the
  environment. A **separate cloud key** (1 year) keeps the owner's main key off the cloud and can be
  revoked alone.
- Environment variables are **not** available to the setup script, only to the session. Unlocking
  therefore happens in `SessionStart`, which also keeps the tree fresh despite the setup cache.
- `CLAUDE.md` is loaded before hooks run, so the hook tells Claude to read it.
- The harness sets `user.signingkey` to an ssh key; gcrypt signs with gpg, so the hook sets
  `remote.origin.gcrypt-signingkey`.
- The harness gives each session a `claude/...` branch. That is fine: the local branch keeps the
  harness name, the encrypted repo only has `main`, and `Stop` pushes `HEAD:main`. Pull requests
  cannot work on an encrypted repo, GitHub sees no files.
- A plain `git push` to the GitHub URL would upload the whole ICM unencrypted. `pre-push`
  blocks it; only gcrypt's own `refs/gcrypt/*` push goes to the plain URL.
- A `git fetch` inside `pre-push` during a gcrypt push corrupts the remote ("Packfile does not
  match digest"). Freshness is checked before the push, never inside the hook.
- In a routine run the runner rewrites `origin` back to the plain GitHub URL after the hook, so the
  gcrypt remote is named **icm** in the cloud (a routine otherwise fetched `main` from the raw repo,
  which only holds gcrypt's `master`; seen 2026-09-17). On a laptop it stays `origin`.

## Setup, per user (admin)

Prerequisites on the admin Mac: the user's ICM repo with `origin` = `gcrypt::git@github.com:<owner>/<repo>.git`,
their main GPG key present, `git-remote-gcrypt`, and `.githooks/pre-push` from this skill with
`git config core.hooksPath .githooks`. The Claude GitHub app must have access to the repo.

1. Inside the user's ICM repo:
   ```bash
   bash core/adapters/claude/scripts/make-cloud-setup.sh "<Name> ICM"
   ```
   It creates the cloud key, adds it as recipient, pushes, and writes a setup script to `$TMPDIR`.
   To regenerate the script for an existing key: add its fingerprint as second argument.
2. On claude.ai/code, logged in as **the user**: create the environment with that name, network
   access Trusted, paste the setup script.
3. Copy the key without seeing it: `gpg --export-secret-keys --armor <fpr> | base64 | pbcopy`, and add
   one line to the environment variables: `ICM_GPG_KEY=<paste>`. No quotes.
4. Calendar reminder a week before the key expires.
5. Test on the user's phone: new session, pick the environment **and** the ICM repo, ask "what do
   you see?", then ask for a small change and check it arrives with `git pull` on the Mac.

## What the user needs to know

Only this: when starting a session, pick the environment "<Name> ICM" and the ICM repository.
Everything is saved after each reply. If Claude says the ICM is not available, it also says what
to do.

## Failure modes and what handles them

| Failure | Handled by |
| --- | --- |
| wrong or no environment, key missing or damaged | `SessionStart` prints `ICM NOT AVAILABLE` and one sentence for the user; Claude must not touch files |
| network down, key expired, GitHub unreachable | same, with "try again in a few minutes" |
| user thinks it is saved but nothing was committed | `Stop` blocks once and asks Claude to commit; second pass autosaves |
| resumed session after days | `SessionStart` rebases with autostash; it resets only on first start (`.git/icm-unlocked`) |
| same record changed on phone and laptop | rebase conflict: Claude shows both versions and asks the user which is right |
| push fails | `Stop` tells the user in one sentence; retried after the next reply, never loops |
| push to plain GitHub URL, or to a branch other than main | `pre-push` refuses |
| setup apt mirror flakes | setup retries three times |
| harness asks to push commits that are already on `icm/main` | `SessionStart` patches `~/.claude/stop-hook-git-check.sh` to bail on a gcrypt checkout |

Commit messages are proportional: one line for a small change, a short body only when something
substantial changed.

### The harness stop hook asks for a push that must never happen

The runner ships its own `~/.claude/stop-hook-git-check.sh`, which compares the branch against
`origin` and, after every reply, asks for a push. On an ICM checkout `origin` is the plain GitHub
URL and is deliberately never pushed to, so the count only grows: 255 unpushed commits on a branch
in sync with `icm/main` (2026-09-19). `stop-sync.sh` already commits and pushes, so the generic
check is redundant here, not merely noisy, and a false alarm every single reply is one that stops
being read.

`session-start.sh` patches it at every session start, guarded by an `ICM-GCRYPT` marker. Not once
in the setup script: the runner writes that file fresh per session, and the setup script itself
runs only at container creation and is then cached for about a week.

### What the cloud runner does not have

Ubuntu 24.04, and no ImageMagick, ffmpeg, yt-dlp or tiktoken unless the setup script installs
them. The setup script does, but nothing may depend on it: a cached container predates any change
to that script, so a routine that needs a binary fails on a machine that looks identical.

A page-building skill learned this the hard way on 2026-09-19: the morning routine wrote its record
and then died on `FileNotFoundError: 'magick'`, leaving yesterday's page on the phone. It now reads
image and video dimensions out of the file header itself and treats the external tool as a fallback.

**Installing the package would not have fixed it.** Ubuntu 24.04 ships ImageMagick 6, which has
`convert` and `identify` and no `magick` binary at all; `magick` is ImageMagick 7. Reach for the
header, or call both names, before reaching for apt.

## Lost phone, compromised account, yearly replacement

```bash
bash core/adapters/claude/scripts/revoke-cloud-key.sh <fingerprint>
```

Removes the key as recipient and re-encrypts the whole remote with `GCRYPT_FULL_REPACK=1`, so the
old key opens nothing on the remote afterwards. Copies taken before revocation stay readable. Then
delete `ICM_GPG_KEY` from the environment and, if needed, run `make-cloud-setup.sh` for a new key.

## Files

- `hooks/pre-push`: symlinked from the ICM repo's `.githooks/pre-push`.
- `hooks/session-start.sh`, `hooks/stop-sync.sh`: embedded into the setup script by the generator.
- `make-cloud-setup.sh` and `revoke-cloud-key.sh` in `scripts/`: run by the admin on a Mac.
