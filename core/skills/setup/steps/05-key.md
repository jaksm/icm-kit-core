# 05 Key

The owner's encryption key, and an honest account of what it does.

## Detect

`gpg --list-secret-keys --with-colons | grep -c '^sec'` prints `1` or more, and the owner confirms
which key is meant for the ICM. An existing key is used, not replaced.

## Ask

Nothing new: name and email are in git config from step 03.

## Do

Explain first, from `references/explain-encryption.md` and `references/what-the-provider-sees.md`,
in their manner. They must leave this step knowing three things:

1. The key protects the ICM **if the repo or the hosting account is stolen**. The host only ever stores an encrypted blob.
2. It does **not** hide anything from the AI provider: whatever the agent reads in a session is sent
   to the model. What the provider keeps, and for how long, is in the adapter's `SKILL.md`. Have
   them open the provider's privacy setting now and decide about model training on purpose.
3. **Lose the key or forget the passphrase and the ICM cannot be recovered** by anyone. Step 07 exists because of this.

Then:

```bash
gpg --quick-generate-key "<name> <<email>>" future-default default never
```

A window asks for a passphrase. **They choose and type it; you never see it.** Tell them before
you run the command that the window will appear, and to pick something they will still know in a year.

## Checkpoint

The passphrase window. Also: if they already keep keys, which one to use.

## Writes

`git config user.signingkey <fingerprint>`. Nothing about the key goes into any file of the ICM.

## Proof

```bash
gpg --list-secret-keys --with-colons | awk -F: '/^fpr/{print $10; exit}'      # a 40 character fingerprint
ls "${GNUPGHOME:-$HOME/.gnupg}/openpgp-revocs.d/"                                               # <fingerprint>.rev exists
```
