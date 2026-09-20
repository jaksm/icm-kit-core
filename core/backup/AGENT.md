# Recovery USB of an ICM

The owner pointed you at this USB to put their ICM on a new computer. Before you talk, open the
instruction file at the root of `icm/<name>/` on this stick and read the record it names first
(`how-we-talk.md`, or what this owner calls it): it says which language they use and how much they
want explained. `usb.env` holds the key fingerprint, the remote and the folder name.

| Path | What it is |
| --- | --- |
| `key/secret-key.asc` | the GPG key the repo is encrypted with |
| `key/revocation.rev` | revocation certificate; only if the key leaks |
| `icm/<name>/` | the whole ICM as plain files, as of the day in `usb.env` |
| `icm/<name>.bundle` | the same with full history, for `git clone` without the host |
| `tools/git-remote-gcrypt` | the encryption helper; on Windows it is copied from here |
| `restore-mac.sh`, `restore-windows.ps1` | do everything below |

**Never ask for the key passphrase in the conversation and never write it to a file.** When
pinentry appears, the owner types it.

## In order

The two restore scripts are unverified in this form: run them, but check each result as you go
(`core/RECIPES.md` in the ICM says how).

1. Mac: `bash <USB>/restore-mac.sh`. Windows: `restore-windows.ps1`. It installs what is missing,
   imports the key, logs in to the host in the browser, clones, and writes the gcrypt settings.
2. If the host cannot be reached: `git clone <USB>/icm/<name>.bundle ~/<name>`, then
   `git remote set-url origin gcrypt::<REPO from usb.env>` and the same `git config` lines as in the script.
3. Verify: `git -C ~/<name> log --oneline | head -3` and `git ls-remote origin`.
4. With several GPG keys on the machine, `git config remote.origin.gcrypt-publish-participants true`
   keeps gpg from trying the wrong ones.
5. Open the instruction file at the root of `~/<name>` and carry on from the ICM. The USB is no longer needed.

| If it fails | Say and do |
| --- | --- |
| the clone is empty | the host account has no access to the repo; delete the folder, fix access, rerun |
| pinentry never appears, signing hangs | `gpgconf --kill gpg-agent`, open a new terminal so `GPG_TTY` is set |
| the stick is older than the last work | fine: the clone comes from the host, the stick only carries the key |
