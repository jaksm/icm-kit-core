#!/usr/bin/env bash
# Put this release of core/ into an ICM repo and record what was put there.
#   ./install.sh <repo>            first install, or update when nothing in core/ was edited locally
#   ./install.sh <repo> --status   list files the owner changed since the last install; writes nothing
#   ./install.sh <repo> --force    update anyway; locally edited files are saved as <file>.local first
# invariant: core.lock is the only record of what the owner was given. Without it an update cannot
# tell a local edit from an old release, so it is rewritten on every install and never by hand.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
repo="${1:?usage: install.sh <repo> [--status|--force]}"; mode="${2:-}"
[ -d "$repo/.git" ] || { echo "install: $repo is not a git repo"; exit 1; }
lock="$repo/core.lock"
sum() { shasum -a 256 "$1" | cut -d' ' -f1; }

edited=()
if [ -f "$lock" ]; then
  while read -r hash path; do
    [ "$hash" = version ] && continue
    [ -f "$repo/$path" ] || { edited+=("$path (deleted)"); continue; }
    [ "$(sum "$repo/$path")" = "$hash" ] || edited+=("$path")
  done < "$lock"
fi
if [ "$mode" = --status ]; then
  echo "installed: $( [ -f "$lock" ] && sed -n 's/^version //p' "$lock" || echo none), available: $(cat "$here/VERSION")"
  echo "locally edited files: ${#edited[@]}"; [ ${#edited[@]} -eq 0 ] || printf '  %s\n' "${edited[@]}"
  exit 0
fi
if [ ${#edited[@]} -gt 0 ] && [ "$mode" != --force ]; then
  echo "install: ${#edited[@]} files in core/ were edited since the last install:"; printf '  %s\n' "${edited[@]}"
  echo "install: read MIGRATIONS/, decide what to keep, then rerun with --force (edited files are kept as <file>.local)"
  exit 1
fi
for e in ${edited[@]+"${edited[@]}"}; do [ -f "$repo/$e" ] && cp "$repo/$e" "$repo/$e.local"; done

mkdir -p "$repo/core"
rsync -a --delete --exclude '*.local' --exclude __pycache__ "$here/core/" "$repo/core/"
{ echo "version $(cat "$here/VERSION")"
  (cd "$repo" && find core -type f ! -name '*.local' ! -path '*/__pycache__/*' | LC_ALL=C sort | while read -r f; do echo "$(sum "$f") $f"; done)
} > "$lock"
echo "install: core $(cat "$here/VERSION") in $repo, $(($(wc -l < "$lock") - 1)) files locked"
