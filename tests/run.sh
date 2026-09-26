#!/usr/bin/env bash
# Tests for install.sh: the one script that runs inside somebody else's ICM. Usage: tests/run.sh [case]
# Every case gets a fresh git repo with witness files outside core/, and the first rule is checked
# after every case: nothing outside core/ and core.lock is ever touched.
# Output: one line per case, `ok <name>` or `FAIL <name>: why`. Exit 0 when all pass, 1 otherwise.
# Old releases come from `git archive v<X>`, so the tags are part of what is tested.
set -u
# invariant: run from a commit hook, git exports GIT_DIR and GIT_INDEX_FILE, and every git command in a
# test would then act on THIS repo instead of the temporary one. They are dropped first.
unset $(git rev-parse --local-env-vars 2>/dev/null)
here="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
only="${1:-}"; failed=0; ran=0

release() {  # release <tag> -> a folder holding that release, extracted once
  local d="$tmp/rel-$1"
  [ -d "$d" ] || { mkdir -p "$d" && git -C "$here" archive "$1" | tar -x -C "$d"; } || return 1
  echo "$d"
}
icm() {  # a fresh ICM with witnesses; the name may hold a space
  local d="$tmp/${1:-icm}-$RANDOM"
  mkdir -p "$d/_config" "$d/domains/a" "$d/.githooks"
  git -C "$d" init -q
  echo '{"mine": 1}' > "$d/_config/own.json"; echo "# mine" > "$d/domains/a/CONTEXT.md"; echo "#!/bin/sh" > "$d/.githooks/pre-commit"
  echo "$d"
}
tree_hash() { (cd "$1" && find "${@:2}" -type f ! -path './.git/*' 2>/dev/null | LC_ALL=C sort | xargs shasum -a 256 2>/dev/null | shasum -a 256 | cut -d' ' -f1); }
witness() { tree_hash "$1" _config domains .githooks; }

run() {  # run <name> <function>
  [ -z "$only" ] || [ "$only" = "$1" ] || return 0
  ran=$((ran + 1)); local why
  if why="$("$2" 2>&1)"; then echo "ok $1"; else echo "FAIL $1: $(echo "$why" | tail -3 | tr '\n' ' ')"; failed=$((failed + 1)); fi
}
must() { "$@" || { echo "expected to hold: $*"; return 1; }; }
mustnot() { ! "$@" || { echo "expected NOT to hold: $*"; return 1; }; }

t_first_install() {
  local d w; d="$(icm)"; w="$(witness "$d")"
  must "$here/install.sh" "$d" >/dev/null || return 1
  must grep -q "^version $(cat "$here/VERSION")$" "$d/core.lock" || return 1
  local files locked; files="$(cd "$d" && find core -type f | wc -l | tr -d ' ')"; locked="$(grep -vc '^version \|^module ' "$d/core.lock")"
  [ "$files" = "$locked" ] || { echo "core/ has $files files, the lock $locked"; return 1; }
  mustnot grep -q '__pycache__\|\.local$' "$d/core.lock" || return 1
  [ "$w" = "$(witness "$d")" ] || { echo "files outside core/ changed"; return 1; }
}
t_idempotent() {
  local d; d="$(icm)"; "$here/install.sh" "$d" >/dev/null; cp "$d/core.lock" "$tmp/lock1"
  "$here/install.sh" "$d" >/dev/null; must cmp -s "$d/core.lock" "$tmp/lock1"
}
t_status() {
  local d out; d="$(icm)"; "$here/install.sh" "$d" >/dev/null
  out="$("$here/install.sh" "$d" --status)"; echo "$out" | grep -q "locally edited files: 0" || { echo "clean status: $out"; return 1; }
  echo "# mine" >> "$d/core/scripts/link-check.sh"; rm "$d/core/scripts/remind.sh"
  out="$("$here/install.sh" "$d" --status)"
  echo "$out" | grep -q "locally edited files: 2" && echo "$out" | grep -q "core/scripts/link-check.sh$" && echo "$out" | grep -q "remind.sh (deleted)" || { echo "$out"; return 1; }
}
t_edited_blocks() {
  local d before w; d="$(icm)"; "$here/install.sh" "$d" >/dev/null
  echo "# mine" >> "$d/core/scripts/link-check.sh"; before="$(tree_hash "$d" core core.lock)"; w="$(witness "$d")"
  mustnot "$here/install.sh" "$d" >/dev/null || return 1
  [ "$before" = "$(tree_hash "$d" core core.lock)" ] || { echo "a refused install changed core/"; return 1; }
  # invariant: --add and --remove are refused as a whole too, not half applied before the refusal
  mustnot "$here/install.sh" "$d" --add import >/dev/null || return 1
  [ "$before" = "$(tree_hash "$d" core core.lock)" ] || { echo "a refused --add changed core/"; return 1; }
  [ "$w" = "$(witness "$d")" ] || { echo "files outside core/ changed"; return 1; }
}
t_force_keeps_local() {
  local d; d="$(icm)"; "$here/install.sh" "$d" >/dev/null
  echo "# mine" >> "$d/core/scripts/link-check.sh"
  must "$here/install.sh" "$d" --force >/dev/null || return 1
  must grep -q "# mine" "$d/core/scripts/link-check.sh.local" || return 1
  must cmp -s "$d/core/scripts/link-check.sh" "$here/core/scripts/link-check.sh" || return 1
  mustnot grep -q '\.local' "$d/core.lock" || return 1
  must "$here/install.sh" "$d" >/dev/null || return 1          # the next update is clean and keeps the copy
  must test -f "$d/core/scripts/link-check.sh.local"
}
t_add_remove() {
  local d before; d="$(icm)"; "$here/install.sh" "$d" --add import --add expenses >/dev/null
  must test -f "$d/core/workflows/import/SKILL.md" || return 1
  must grep -q "^module expenses$" "$d/core.lock" || return 1
  "$here/install.sh" "$d" >/dev/null; must test -f "$d/core/workflows/expenses/SKILL.md" || { echo "a plain update dropped a workflow"; return 1; }
  "$here/install.sh" "$d" --remove import >/dev/null
  mustnot test -e "$d/core/workflows/import" || return 1
  mustnot grep -q "^module import$\|core/workflows/import/" "$d/core.lock" || return 1
  must test -f "$d/core/workflows/expenses/SKILL.md" || return 1
  before="$(tree_hash "$d" core core.lock)"
  mustnot "$here/install.sh" "$d" --add no-such-thing >/dev/null || return 1
  [ "$before" = "$(tree_hash "$d" core core.lock)" ] || { echo "an unknown workflow changed core/"; return 1; }
}
t_remove_edited_workflow() {
  # the owner changed a file of a workflow and then removes the workflow: their edit must survive somewhere
  local d; d="$(icm)"; "$here/install.sh" "$d" --add import >/dev/null
  echo "my rule" >> "$d/core/workflows/import/SKILL.md"
  mustnot "$here/install.sh" "$d" --remove import >/dev/null || { echo "removed a workflow with an edited file without --force"; return 1; }
  must grep -q "my rule" "$d/core/workflows/import/SKILL.md" || return 1
  must "$here/install.sh" "$d" --remove import --force >/dev/null || return 1
  mustnot test -e "$d/core/workflows/import" || return 1
  must grep -q "my rule" "$d/core/workflows/import.local/SKILL.md" || return 1
  must "$here/install.sh" "$d" >/dev/null || return 1
  must test -f "$d/core/workflows/import.local/SKILL.md"
}
t_update_040_with_sources() {
  local d old w; old="$(release v0.4.0)" || return 1; d="$(icm)"
  "$old/install.sh" "$d" --add sources --add expenses >/dev/null; w="$(witness "$d")"
  must test -f "$d/core/workflows/sources/scripts/check-feed.py" || return 1
  must "$here/install.sh" "$d" >/dev/null || return 1
  mustnot test -e "$d/core/workflows/sources/scripts/check-feed.py" || return 1
  must test -f "$d/core/scripts/check-feed.py" || return 1
  must grep -q "^module sources$" "$d/core.lock" && must test -f "$d/core/workflows/expenses/SKILL.md" || return 1
  "$here/install.sh" "$d" --status | grep -q "locally edited files: 0" || { echo "edited files after a clean update"; return 1; }
  [ "$w" = "$(witness "$d")" ] || { echo "files outside core/ changed"; return 1; }
}
t_every_release_in_turn() {
  local d tags t r; d="$(icm)"; tags="$(git -C "$here" tag | grep '^v[0-9]' | sort -V)"
  for t in $tags; do
    r="$(release "$t")" || return 1
    "$r/install.sh" "$d" >/dev/null || { echo "update to $t failed"; return 1; }
    "$r/install.sh" "$d" --status | grep -q "locally edited files: 0" || { echo "$t: edited files after a clean update"; return 1; }
  done
  must "$here/install.sh" "$d" >/dev/null
}
t_not_a_repo() {
  local d out; d="$tmp/plain-$RANDOM"; mkdir -p "$d"
  out="$("$here/install.sh" "$d" 2>&1)" && { echo "installed into a folder that is not a repo"; return 1; }
  echo "$out" | grep -q "not a git repo" || { echo "$out"; return 1; }
  mustnot test -e "$d/core"
}
t_path_with_space() {
  local d; d="$(icm "my icm")"
  must "$here/install.sh" "$d" --add import >/dev/null || return 1
  must test -f "$d/core/workflows/import/SKILL.md" || return 1
  echo "# mine" >> "$d/core/scripts/link-check.sh"
  must "$here/install.sh" "$d" --force >/dev/null || return 1
  must test -f "$d/core/scripts/link-check.sh.local"
}
t_worktree() {
  local d wt; d="$(icm)"; git -C "$d" -c user.email=t@example.com -c user.name=t commit -q --allow-empty -m init
  wt="$tmp/wt-$RANDOM"; git -C "$d" worktree add -q "$wt" -b side >/dev/null 2>&1 || return 1
  must "$here/install.sh" "$wt" >/dev/null || return 1
  must test -f "$wt/core.lock"
}
t_workflow_gone_from_catalog() {
  local d out; d="$(icm)"; "$here/install.sh" "$d" >/dev/null
  mkdir -p "$d/core/workflows/retired"; echo "kept" > "$d/core/workflows/retired/SKILL.md"
  sed -i.bak '1a\
module retired' "$d/core.lock" && rm "$d/core.lock.bak"
  out="$("$here/install.sh" "$d" --force 2>&1)" || { echo "$out"; return 1; }
  echo "$out" | grep -q "no longer in the catalog" || { echo "$out"; return 1; }
  must grep -q "kept" "$d/core/workflows/retired/SKILL.md"
}
t_pages_build_from_demo() {
  # invariant: both page builders fill a self-contained template from mock data, with no library and no leftover slot
  local out; out="${TMPDIR:-/tmp}/icm-kit-demo"; rm -rf "$out"
  must python3 "$here/core/workflows/graph/scripts/build-graph-page.py" --demo >/dev/null || return 1
  must python3 "$here/catalog/expenses/scripts/build-expenses-page.py" --demo >/dev/null || return 1
  must python3 "$here/catalog/expenses/scripts/build-expenses-page.py" --check >/dev/null || return 1
  local f; for f in graph expenses; do
    must test -s "$out/$f.html" || return 1
    mustnot grep -q 'icm-\|ICM-\|{{\|__DATA__\|__TABS__' "$out/$f.html" || { echo "$f.html holds a leftover slot or library class"; return 1; }
    must grep -q 'prefers-color-scheme' "$out/$f.html" || return 1
  done
  rm -rf "$out" "$here/pages"
}
t_release_is_documented() {
  local v; v="$(cat "$here/VERSION")"
  must grep -q "^## $v" "$here/CHANGELOG.md" || return 1
  ls "$here/MIGRATIONS" | grep -q -- "-$v.md$" || { echo "no MIGRATIONS/<from>-$v.md"; return 1; }
}

run first-install t_first_install
run idempotent t_idempotent
run status t_status
run edited-blocks t_edited_blocks
run force-keeps-local t_force_keeps_local
run add-remove t_add_remove
run remove-edited-workflow t_remove_edited_workflow
run update-0.4.0-with-sources t_update_040_with_sources
run every-release-in-turn t_every_release_in_turn
run not-a-repo t_not_a_repo
run path-with-space t_path_with_space
run worktree t_worktree
run workflow-gone-from-catalog t_workflow_gone_from_catalog
run pages-build-from-demo t_pages_build_from_demo
run release-is-documented t_release_is_documented
[ "$ran" -gt 0 ] || { echo "no case named '$only'"; exit 2; }
echo "$((ran - failed)) of $ran passed"
[ "$failed" -eq 0 ]
