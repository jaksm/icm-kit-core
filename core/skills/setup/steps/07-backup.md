# 07 Backup (recommended, not required)

## Detect

`domains/system/output/connectors-and-routines.md` records a backup with a date, or the owner says
they already keep the key somewhere safe and can say where.

## Ask

Explain the one fact: without the key the ICM is gone, and the computer holding the only copy can
be lost, stolen or wiped. Then recommend the recovery USB and let them decide:

- **Recovery USB** (recommended): the key, its revocation certificate, the whole repo with history,
  and everything a new computer needs, including instructions for the agent there.
- **Their own way**: a password manager or another safe place for the exported key. Fine, if they can say where.
- **Not now**: allowed. Say plainly what they are accepting.

## Do

For the USB: they format a stick as exFAT (name up to 11 characters, no spaces) and plug it in.

```bash
bash core/backup/make-usb.sh /Volumes/<NAME>
```

The passphrase window may appear; it is theirs. Then tell them to keep the stick **away from the
computer it backs up**, and that whoever holds the stick and the passphrase can read everything.

For their own way: `gpg --export-secret-keys --armor <fingerprint>` straight into the place they
chose, never into the ICM folder and never into the conversation.

## Checkpoint

The choice itself. If they skip, write `skipped` with their reason and add a line to
`domains/system/output/open-tasks.md`. The minimum even then: confirm that
`~/.gnupg/openpgp-revocs.d/<fingerprint>.rev` exists and that they know it is what cancels a leaked key.

## Writes

`domains/system/output/connectors-and-routines.md`: what kind of backup, the date, and where it is
kept **in their words** ("the drawer at my sister's"), never a path to a secret.

## Proof

`make-usb.sh` ended with `ready at ... bundle verified`, and `ls <USB>/key/` shows `secret-key.asc`,
`public-key.asc`, `revocation.rev`.
