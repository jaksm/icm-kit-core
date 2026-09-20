# Material: encryption

Facts to explain from. Pick what the owner's chosen depth needs, say it in their manner.

- The ICM on the computer is plain files. Encryption happens at the moment of pushing: everything,
  including file names, history and branch names, leaves the machine as one encrypted blob.
- The host stores that blob. Someone who steals the hosting account, or the host itself, sees
  hexadecimal names and noise. A private repo is a second, weaker layer on top.
- The key has two halves. The public half locks; the secret half, guarded by the passphrase,
  unlocks. The secret half lives in `~/.gnupg` on this computer and nowhere else until a backup is made.
- A key can have several participants. The cloud key in step 08 is a second participant with a
  one year life, so the main key never leaves the computer and the cloud one can be cancelled alone.
- Cancelling a participant re-encrypts the remote, so the old key opens nothing **from then on**.
  Copies taken before that stay readable. Revocation limits damage; it does not undo it.
- The revocation certificate is a file that says "this key is no longer mine". It is only useful if the key leaks.

Everyday comparisons that hold up: a safe deposit box whose bank cannot open it; a diary in a
language only you read, mailed to yourself. One that does not: "the cloud is a backup" (it is, but
only of noise, without the key).

Limits to say plainly: see `what-the-provider-sees.md`.
