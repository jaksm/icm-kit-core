#!/usr/bin/env bash
# Claude Code Stop hook for a cloud session: after every reply the ICM change is committed and pushed, so nothing lives only in the session.
# invariant: blocks at most once per reply (stop_hook_active), otherwise a failing push would loop forever; the second pass saves what it can and lets Claude stop.
set -u
input=$(cat)
cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0
[ -f .git/icm-unlocked ] || exit 0
again=$(printf '%s' "$input" | grep -c '"stop_hook_active": *true')

block() {
  [ "$again" -gt 0 ] && { echo "$1" >&2; exit 0; }
  python3 -c 'import json,sys; print(json.dumps({"decision":"block","reason":sys.argv[1]}))' "$1"
  exit 0
}
conflict() {
  block "ICM SYNC CONFLICT in: $(git diff --name-only --diff-filter=U | tr '\n' ' ')
The same record was changed here and somewhere else. For each file show the user both versions (git show :2:<file> is the ICM, :3:<file> is this session) in plain words and ask which one is right. Apply the answer, git add, git rebase --continue. Do not push."
}

{ [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; } && conflict

if [ -n "$(git status --porcelain)" ]; then
  [ "$again" -eq 0 ] && block "The ICM has uncommitted changes. Commit them now. Keep the message proportional: one line for a small change, a short body only when something substantial changed or a fact was replaced. Do not push."
  git add -A && git commit -q --no-verify -m "Autosave from cloud session"
fi

git fetch -q icm main 2>/dev/null || block "The ICM could not be reached, so the latest change is saved in this session but not yet in the ICM. Tell the user in one sentence; it is retried after the next reply."
[ -n "$(git log --oneline icm/main..HEAD)" ] || exit 0
git rebase -q icm/main >/dev/null 2>&1 || conflict
err=$(git push -q icm HEAD:main 2>&1) || block "Push failed: $(printf '%s' "$err" | tail -2). Tell the user in one sentence that the latest change is saved in this session but not yet in the ICM; it is retried after the next reply."
exit 0
