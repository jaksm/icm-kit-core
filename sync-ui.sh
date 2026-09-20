#!/usr/bin/env bash
# Vendor a release of icm-ui into core/ui. Usage: ./sync-ui.sh [path-to-icm-ui]   (default: ../icm-ui)
# invariant: core/ui is a copy, never edited here. A fix goes to icm-ui and comes back through this script.
set -eu
cd "$(dirname "$0")"
src="${1:-../icm-ui}"
[ -f "$src/build.py" ] || { echo "sync-ui: $src is not icm-ui"; exit 1; }
(cd "$src" && python3 build.py --check >/dev/null) || { echo "sync-ui: icm-ui does not pass its own check"; exit 1; }
rsync -a --delete --exclude .git --exclude __pycache__ --exclude node_modules --exclude .gitignore "$src/" core/ui/
echo "sync-ui: core/ui is icm-ui $(cat core/ui/VERSION)"
