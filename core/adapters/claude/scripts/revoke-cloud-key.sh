#!/usr/bin/env bash
# Revoke a cloud key of an encrypted ICM (lost phone, compromised Claude account, yearly replacement): drop it as recipient and re-encrypt the whole remote.
# invariant: GCRYPT_FULL_REPACK re-encrypts every pack with new keys, so the revoked key opens nothing that is on the remote afterwards; copies taken before stay readable.
# Usage: revoke-cloud-key.sh <fingerprint>   (run inside the ICM repo, then delete ICM_GPG_KEY from the cloud environment)
set -euo pipefail
fpr="${1:?usage: revoke-cloud-key.sh <fingerprint>}"
cd "$(git rev-parse --show-toplevel)"
participants=$(git config remote.origin.gcrypt-participants)
case " $participants " in *" $fpr "*) ;; *) echo "$fpr is not a recipient of origin" >&2; exit 1 ;; esac
rest=$(printf '%s\n' $participants | grep -vx "$fpr" | tr '\n' ' ')
[ -n "${rest// /}" ] || { echo "refusing to remove the last recipient" >&2; exit 1; }

git config remote.origin.gcrypt-participants "${rest% }"
git pull -q --rebase origin main
git commit -q --allow-empty -m "Revoke cloud key $fpr"
GCRYPT_FULL_REPACK=1 git push -q origin main
gpg --batch --yes --delete-secret-and-public-key "$fpr" 2>/dev/null || true
echo "Revoked $fpr. Now delete ICM_GPG_KEY from the cloud environment; for a new key run make-cloud-setup.sh."
