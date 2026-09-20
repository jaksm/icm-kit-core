#!/usr/bin/env bash
# Run by the owner inside their ICM repo, on their computer: makes a cloud-only GPG key, adds it to the encrypted remote, and writes the setup script for claude.ai/code.
# invariant: the private key is never printed or written into a file; it only goes to the clipboard, on explicit request.
# Usage: make-cloud-setup.sh "Environment name" [existing cloud key fingerprint]   (with a fingerprint: only regenerate the setup script)
set -euo pipefail
env_name="${1:?usage: make-cloud-setup.sh \"Environment name\" [fingerprint] (run inside the ICM repo)}"
reuse="${2:-}"
here="$(cd "$(dirname "$0")/.." && pwd)"
cd "$(git rev-parse --show-toplevel)"

git remote get-url origin | grep -q '^gcrypt::' || { echo "origin is not a gcrypt:: remote; set up the encrypted remote first" >&2; exit 1; }
name=$(git config user.name); email=$(git config user.email)
participants=$(git config remote.origin.gcrypt-participants)

if [ -n "$reuse" ]; then
  fpr=$reuse
  case " $participants " in *" $fpr "*) participants=$(printf '%s\n' $participants | grep -vx "$fpr" | tr '\n' ' ') ;;
    *) echo "$fpr is not a recipient of origin" >&2; exit 1 ;; esac
else
  gpg --batch --pinentry-mode loopback --passphrase '' --quick-generate-key "ICM cloud ($name) <$email>" ed25519 sign 1y 2>/dev/null
  fpr=$(gpg --list-keys --with-colons "ICM cloud ($name)" | awk -F: '/^fpr/{f=$10} END{print f}')
  gpg --batch --pinentry-mode loopback --passphrase '' --quick-add-key "$fpr" cv25519 encr 1y 2>/dev/null
  git config remote.origin.gcrypt-participants "$participants $fpr"
  git commit -q --allow-empty -m "Add cloud key $fpr to the encrypted remote"
  git pull -q --rebase origin main
  git push -q origin main
fi
expires=$(date -r "$(gpg --list-keys --with-colons "$fpr" | awk -F: '/^pub/{print $7; exit}')" +%F)

out="${TMPDIR:-/tmp}/icm-cloud-setup-$(date +%Y%m%d-%H%M%S).sh"
{
  echo '#!/bin/bash'
  echo "# Setup script for the Claude Code cloud environment \"$env_name\". Paste into the environment's setup script field."
  echo '# Runs once and is cached for about 7 days, without environment variables; unlocking happens in the SessionStart hook.'
  echo 'set -e'
  # imagemagick and ffmpeg are a FALLBACK, not a requirement: the feed builder reads image
  # and video dimensions from the file header itself. Ubuntu 24.04 ships ImageMagick 6, which
  # has no `magick` binary at all, so installing the package would NOT have fixed the crash
  # that made this line grow (2026-09-19); they stay for formats the reader does not know.
  echo '# ICM: imagemagick/ffmpeg are a fallback for formats the header reader does not know.'
  echo 'for i in 1 2 3; do apt-get update -qq && apt-get install -y -qq gnupg git-remote-gcrypt imagemagick ffmpeg >/dev/null && break; sleep 5; done'
  echo 'command -v git-remote-gcrypt >/dev/null'
  # tiktoken lets tokeni.py measure instead of estimating; yt-dlp is for uzmi-mediju.py --video.
  # Neither may fail the setup, so the whole line is swallowed.
  echo 'pip3 install -q --break-system-packages tiktoken yt-dlp >/dev/null 2>&1 || true'
  echo 'mkdir -p ~/.claude/icm'
  echo "cat > ~/.claude/icm/config <<'EOF'"
  printf 'ICM_ENV_NAME=%q\nICM_SIGNING_KEY=%s\n' "$env_name" "$fpr"
  echo 'EOF'
  echo "cat > ~/.claude/icm/keys.asc <<'EOF'"
  gpg --export --armor $participants "$fpr" 2>/dev/null
  echo 'EOF'
  echo "cat > ~/.claude/icm/ownertrust.txt <<'EOF'"
  for k in $participants $fpr; do echo "$k:6:"; done
  echo 'EOF'
  for h in session-start.sh stop-sync.sh; do
    # the owner's changed copy of a hook wins over the one in core/ (see recipes/customize.md)
    src="_config/overrides/core/adapters/claude/hooks/$h"; [ -f "$src" ] || src="$here/hooks/$h"
    echo "cat > ~/.claude/icm/$h <<'EOF'"; cat "$src"; echo 'EOF'
  done
  echo "cat > ~/.claude/settings.json <<'EOF'"
  echo '{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"bash ~/.claude/icm/session-start.sh","timeout":300}]}],"Stop":[{"hooks":[{"type":"command","command":"bash ~/.claude/icm/stop-sync.sh","timeout":300}]}]}}'
  echo 'EOF'
  echo 'echo "ICM setup ok"'
} > "$out"
bash -n "$out"

cat <<EOF
Cloud key: $fpr (expires $expires), recipient of the encrypted remote.

1. Setup script written to: $out
   Paste its content into the setup script of the environment "$env_name" on claude.ai/code.
2. Copy the private key to the clipboard (it is never shown):
     gpg --export-secret-keys --armor $fpr | base64 | pbcopy
   and add it to the same environment as one line: ICM_GPG_KEY=<paste>
3. Put a reminder a week before $expires to replace the key.
4. Test: start a session with "$env_name" and the ICM repository, ask "what do you see?", then ask for a small change.
EOF
