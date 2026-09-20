#!/usr/bin/env bash
# Put the ICM from this USB on a Mac. Run:  bash "/Volumes/<USB>/restore-mac.sh"
# Safe to run twice: every step checks before it acts.
set -eu
U="$(cd "$(dirname "$0")" && pwd)"
. "$U/usb.env"
command -v brew >/dev/null || { echo "Homebrew is missing. Install it from https://brew.sh and run this again."; exit 1; }
for p in gnupg git-remote-gcrypt pinentry-mac gh; do brew list "$p" >/dev/null 2>&1 || brew install "$p"; done
mkdir -p ~/.gnupg && chmod 700 ~/.gnupg
grep -q pinentry-program ~/.gnupg/gpg-agent.conf 2>/dev/null || echo "pinentry-program $(command -v pinentry-mac)" >> ~/.gnupg/gpg-agent.conf
gpgconf --kill gpg-agent || true
rc="$HOME/.zshrc"; grep -q GPG_TTY "$rc" 2>/dev/null || echo 'export GPG_TTY=$(tty)' >> "$rc"
export GPG_TTY="$(tty || true)"
gpg --import "$U/key/secret-key.asc"
echo "$KEY:6:" | gpg --import-ownertrust
# GitHub login in the browser, once
gh auth status >/dev/null 2>&1 || gh auth login --web --git-protocol ssh
gh auth setup-git
[ -d "$HOME/$NAME" ] || git clone "gcrypt::$REPO" "$HOME/$NAME"
cd "$HOME/$NAME"
git log -1 >/dev/null 2>&1 || { echo "ERROR: the clone is empty. Usually the GitHub account has no access to the repo. Delete $HOME/$NAME, fix access, run again. Offline: git clone \"$U/icm/$NAME.bundle\" \"$HOME/$NAME\""; exit 1; }
git config remote.origin.gcrypt-participants "$KEY"
git config remote.origin.gcrypt-signingkey "$KEY"
git config user.signingkey "$KEY"
git config remote.origin.gcrypt-publish-participants true
git config core.hooksPath .githooks
echo "DONE. The ICM is in $HOME/$NAME"
