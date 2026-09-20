#!/usr/bin/env bash
# Make or refresh a recovery USB for this ICM: the key, its revocation certificate, the whole repo with history, and what a new machine needs.
#   bash core/backup/make-usb.sh /Volumes/MYICM        (format the stick as exFAT first; name up to 11 characters, no spaces)
# invariant: the passphrase is never asked for here and never written anywhere. If gpg needs it, pinentry asks the owner.
# invariant: nothing about the owner is hardcoded. Key and remote are read from this repo's git config and written to usb.env.
set -eu
U="${1:?usage: make-usb.sh <path to the mounted USB>}"
cd "$(git rev-parse --show-toplevel)"
[ -d "$U" ] || { echo "make-usb: $U does not exist; is the stick mounted?"; exit 1; }
KEY="$(git config remote.origin.gcrypt-signingkey || git config user.signingkey || true)"
URL="$(git config remote.origin.url || true)"
[ -n "$KEY" ] || { echo "make-usb: no signing key in git config; finish the key and remote steps of setup first"; exit 1; }
case "$URL" in gcrypt::*) ;; *) echo "make-usb: origin is not a gcrypt:: remote ($URL)"; exit 1;; esac
NAME="$(basename "$PWD")"

mkdir -p "$U/key" "$U/icm" "$U/tools"
gpg --export-secret-keys --armor "$KEY" > "$U/key/secret-key.asc"
gpg --export --armor "$KEY" > "$U/key/public-key.asc"
rev="${GNUPGHOME:-$HOME/.gnupg}/openpgp-revocs.d/$KEY.rev"
[ -f "$rev" ] && cp "$rev" "$U/key/revocation.rev" || echo "make-usb: no revocation certificate at $rev; make one with: gpg --gen-revoke $KEY"
cp "$(command -v git-remote-gcrypt)" "$U/tools/git-remote-gcrypt"
git bundle create "$U/icm/$NAME.bundle" --all
rsync -a --delete --exclude .git "./" "$U/icm/$NAME/"
printf 'KEY=%s\nREPO=%s\nNAME=%s\nMADE=%s\n' "$KEY" "${URL#gcrypt::}" "$NAME" "$(date +%F)" > "$U/usb.env"
cp core/backup/AGENT.md core/backup/README.txt core/backup/restore-mac.sh core/backup/restore-windows.ps1 "$U/"
find "$U" -name '._*' -delete 2>/dev/null || true
git bundle verify "$U/icm/$NAME.bundle" >/dev/null && [ -s "$U/key/secret-key.asc" ] && echo "make-usb: ready at $U (key $KEY, bundle verified)"
