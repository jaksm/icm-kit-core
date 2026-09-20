#!/usr/bin/env bash
# Put this release of core/ into an ICM and record what was put there.
#   ./install.sh <icm>                 first install, or update when nothing in core/ was edited locally
#   ./install.sh <icm> --status        installed and available version, locally edited files, installed workflows
#   ./install.sh <icm> --add <name>    also install an optional workflow from catalog/ (repeatable)
#   ./install.sh <icm> --remove <name> take an optional workflow out again (with edited files: only with --force, kept as <name>.local)
#   ./install.sh <icm> --force         update although files were edited; they are kept as <file>.local
# invariant: core.lock is the only record of what the owner was given. Without it an update cannot
# tell a local edit from an old release, so it is rewritten on every install and never by hand.
# invariant: the owner's changes never live in core/. They live in _config/, and a changed copy of a
# core file in _config/overrides/<same path>, which the code that uses that file looks at first.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
repo="${1:?usage: install.sh <icm> [--status|--force|--add <name>|--remove <name>]}"; shift
mode=""; add=(); remove=()
while [ $# -gt 0 ]; do
  case "$1" in
    --status|--force) mode="$1" ;;
    --add) add+=("${2:?--add needs a name}"); shift ;;
    --remove) remove+=("${2:?--remove needs a name}"); shift ;;
    *) echo "install: unknown argument $1"; exit 2 ;;
  esac; shift
done
# rev-parse, not a test for .git/: in a worktree .git is a file
git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 || { echo "install: $repo is not a git repo"; exit 1; }
lock="$repo/core.lock"
sum() { shasum -a 256 "$1" | cut -d' ' -f1; }

modules=(); edited=()
if [ -f "$lock" ]; then
  while read -r hash path; do
    case "$hash" in version) continue ;; module) modules+=("$path"); continue ;; esac
    [ -f "$repo/$path" ] || { edited+=("$path (deleted)"); continue; }
    [ "$(sum "$repo/$path")" = "$hash" ] || edited+=("$path")
  done < "$lock"
fi
if [ "$mode" = --status ]; then
  echo "installed: $( [ -f "$lock" ] && sed -n 's/^version //p' "$lock" || echo none), available: $(cat "$here/VERSION")"
  echo "workflows installed from the catalog: ${modules[*]:-none}"
  echo "in the catalog: $(ls "$here/catalog" 2>/dev/null | grep -v '^index.md$' | tr '\n' ' ')"
  echo "locally edited files: ${#edited[@]}"; [ ${#edited[@]} -eq 0 ] || printf '  %s\n' "${edited[@]}"
  left="$(cd "$repo" && find core -name '*.local' 2>/dev/null | LC_ALL=C sort)"
  [ -z "$left" ] || { echo "copies kept by an earlier --force, not yet resolved (git ignores them):"; echo "$left" | sed 's/^/  /'; }
  exit 0   # always 0: read the counts, this is a report and not a gate
fi
for m in ${add[@]+"${add[@]}"}; do
  [ -f "$here/catalog/$m/SKILL.md" ] || { echo "install: no workflow '$m' in the catalog; see catalog/index.md"; exit 1; }
  case " ${modules[*]:-} " in *" $m "*) ;; *) modules+=("$m") ;; esac
done
for m in ${remove[@]+"${remove[@]}"}; do
  keep=(); for x in ${modules[@]+"${modules[@]}"}; do [ "$x" = "$m" ] || keep+=("$x"); done
  modules=(${keep[@]+"${keep[@]}"})
done
if [ ${#edited[@]} -gt 0 ] && [ "$mode" != --force ]; then
  echo "install: ${#edited[@]} files in core/ were edited since the last install:"; printf '  %s\n' "${edited[@]}"
  echo "install: give each edit a home outside core/ first (core/skills/core-update/SKILL.md, step 3), then rerun with --force; edited files are kept as <file>.local"
  exit 1
fi
for e in ${edited[@]+"${edited[@]}"}; do [ -f "$repo/$e" ] && cp "$repo/$e" "$repo/$e.local" && echo "install: kept $e.local"; done
# invariant: nothing is deleted before the check above. A removal used to run first, so taking out a
# workflow whose file the owner had edited destroyed the edit and then refused the install.
# With --force the whole folder is kept beside it as <name>.local, which an update never touches.
for m in ${remove[@]+"${remove[@]}"}; do
  if printf '%s\n' ${edited[@]+"${edited[@]}"} | grep -q "^core/workflows/$m/"; then
    rm -rf "$repo/core/workflows/$m.local" && mv "$repo/core/workflows/$m" "$repo/core/workflows/$m.local"
    echo "install: '$m' had edited files; the folder is kept as core/workflows/$m.local"
  fi
  rm -rf "$repo/core/workflows/$m"
done

mkdir -p "$repo/core"
ex=(); for m in ${modules[@]+"${modules[@]}"}; do ex+=(--exclude "/workflows/$m/"); done
rsync -a --delete --exclude '*.local' --exclude __pycache__ ${ex[@]+"${ex[@]}"} "$here/core/" "$repo/core/"
for m in ${modules[@]+"${modules[@]}"}; do
  [ -d "$here/catalog/$m" ] || { echo "install: workflow '$m' is no longer in the catalog; it stays as it is, see MIGRATIONS/"; continue; }
  mkdir -p "$repo/core/workflows/$m"
  rsync -a --delete --exclude '*.local' --exclude __pycache__ "$here/catalog/$m/" "$repo/core/workflows/$m/"
done
{ echo "version $(cat "$here/VERSION")"
  for m in ${modules[@]+"${modules[@]}"}; do echo "module $m"; done
  (cd "$repo" && find core -type f ! -name '*.local' ! -path '*.local/*' ! -path '*/__pycache__/*' | LC_ALL=C sort | while read -r f; do echo "$(sum "$f") $f"; done)
} > "$lock"
echo "install: core $(cat "$here/VERSION") in $repo, $(grep -vc '^version \|^module ' "$lock") files locked, workflows: ${modules[*]:-none}"
