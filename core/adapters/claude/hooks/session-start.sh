#!/usr/bin/env bash
# Claude Code SessionStart hook for a cloud session: unlock the encrypted ICM, sync it, and say loudly when that did not work.
# invariant: stdout is read by Claude, so every failure prints "ICM NOT AVAILABLE" plus one sentence for the user, and exits 0.
# invariant: the working tree is reset to icm/main only on first start (no .git/icm-unlocked); a resumed session is rebased, never reset, so uncommitted work survives.
# Settings baked in by make-cloud-setup.sh: ~/.claude/icm/config (ICM_ENV_NAME, ICM_SIGNING_KEY), ~/.claude/icm/*.asc, ~/.claude/icm/ownertrust.txt
set -u
. ~/.claude/icm/config
cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0

fail() {
  echo "ICM NOT AVAILABLE: $1"
  echo "Do not read, create or change files in this session. Tell the user, in their language: \"$2\""
  exit 0
}

[ -n "${ICM_GPG_KEY:-}" ] || fail "ICM_GPG_KEY is not set." \
  "This session was started without the ICM environment. Start a new session and choose the environment \"$ICM_ENV_NAME\" and your ICM repository."
gpg --batch --import ~/.claude/icm/*.asc >/dev/null 2>&1
printf '%s' "$ICM_GPG_KEY" | base64 -d 2>/dev/null | gpg --batch --import >/dev/null 2>&1 \
  || fail "ICM_GPG_KEY could not be imported." "The ICM key in the environment settings is damaged and has to be set up again."
gpg --batch --import-ownertrust < ~/.claude/icm/ownertrust.txt >/dev/null 2>&1

# invariant: the gcrypt remote is named icm, not origin. The cloud runner rewrites origin to the plain GitHub URL
# after this hook runs (seen 2026-09-17: fetch then looked for main on the raw repo, which only has gcrypt's master).
raw=$(git remote get-url github-raw 2>/dev/null || git remote get-url origin 2>/dev/null) || fail "the session has no git repository." \
  "This session was started without the ICM repository. Start a new session and choose your ICM repository."
raw=${raw#gcrypt::}
git remote get-url github-raw >/dev/null 2>&1 || { git remote rename origin github-raw; git remote set-url --push github-raw DO-NOT-PUSH-UNENCRYPTED; }
git remote get-url icm >/dev/null 2>&1 && git remote set-url icm "gcrypt::$raw" || git remote add icm "gcrypt::$raw"
git config core.hooksPath .githooks
# the cloud harness sets user.signingkey to an ssh key; gcrypt signs its manifest with gpg and would fail with "No secret key"
git config remote.icm.gcrypt-signingkey "$ICM_SIGNING_KEY"

# The harness ships its own ~/.claude/stop-hook-git-check.sh, which compares the branch against
# origin and asks for a push. Here origin is the plain GitHub URL and is deliberately never
# pushed to, so it reports every commit as unpushed after every single reply; on 2026-09-19 that
# was "255 unpushed commits" on a branch fully in sync with icm/main. stop-sync.sh already
# commits and pushes to icm/main, so the generic check is redundant here, not merely noisy.
# invariant: patched on every session start, not once in the setup script. The harness writes
# that file fresh per session, so a one-time patch would not survive; the ICM-GCRYPT marker
# keeps it idempotent within a session.
h=~/.claude/stop-hook-git-check.sh
if [ -f "$h" ] && ! grep -q ICM-GCRYPT "$h"; then
  { head -1 "$h"
    cat <<'PATCH'
# ICM-GCRYPT: this checkout pushes only to the gcrypt remote named icm; origin is the plain
# GitHub URL and must never be pushed to, so the check below would flag every commit forever.
if git remote get-url icm 2>/dev/null | grep -q '^gcrypt::'; then exit 0; fi
PATCH
    tail -n +2 "$h"
  } > "$h.icm" && mv "$h.icm" "$h" && chmod +x "$h"
fi

err=$(git fetch -q icm main 2>&1) || fail "fetch failed: $(printf '%s' "$err" | tail -1)" \
  "The ICM could not be opened right now, most likely a network problem or an expired key. Try again in a few minutes."

if [ ! -f .git/icm-unlocked ]; then
  branch=$(git branch --show-current); branch=${branch:-main}
  git checkout -q -f -B "$branch" icm/main
  touch .git/icm-unlocked
elif ! git rebase -q --autostash icm/main >/dev/null 2>&1; then
  files=$(git diff --name-only --diff-filter=U | tr '\n' ' ')
  echo "ICM SYNC CONFLICT in: $files"
  echo "The same record was changed in this session and somewhere else. Before anything else, for each file show the user both versions (git show :2:<file> is the ICM, :3:<file> is this session) in plain words, ask which one is right, apply the answer, git add, git rebase --continue."
  exit 0
fi

echo "ICM unlocked in $PWD. Latest change: $(git log -1 --format='%s (%cr)')."
echo "Read CLAUDE.md before your first reply. Commit your changes; do not push, a Stop hook pushes to the encrypted main after every reply. The encrypted remote is named icm; origin is the plain GitHub URL and must never be pushed to."
