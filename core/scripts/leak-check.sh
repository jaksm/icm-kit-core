#!/usr/bin/env bash
# Refuse a commit whose staged changes contain a value from .env or a secret looking string. `--pattern` prints the regex for other gates to reuse.
set -u
PAT='(gh[pousr]_[A-Za-z0-9]{20,}|sk-(proj-|ant-)?[A-Za-z0-9]{32,}|AIza[0-9A-Za-z_-]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|[0-9]{8,10}:[A-Za-z0-9_-]{35}|eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY( BLOCK)?-----)'
[ "${1:-}" = --pattern ] && { printf '%s\n' "$PAT"; exit 0; }
cd "$(git rev-parse --show-toplevel)"
staged=$(git diff --cached --unified=0 --no-color | grep '^+' | grep -v '^+++' || true)
[ -z "$staged" ] && exit 0
hit=0
if [ -f .env ]; then
  while IFS='=' read -r k v; do
    [[ "$k" =~ ^[A-Z0-9_]+$ ]] || continue
    v="${v%\"}"; v="${v#\"}"
    [ -z "$v" ] && continue
    if printf %s "$staged" | grep -qF -- "$v"; then echo "leak-check: staged text contains the value of $k"; hit=1; fi
  done < .env
fi
if printf %s "$staged" | grep -qE "$PAT"; then echo "leak-check: staged text contains a secret looking string"; hit=1; fi
[ $hit -eq 1 ] && echo "leak-check: unstage or redact it, then commit again; git commit --no-verify only for a deliberate exception" && exit 1
exit 0
