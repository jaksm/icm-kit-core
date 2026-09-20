# 02 Machine

Make sure the computer has what an ICM needs, and nothing more.

## Detect

```bash
for t in git gpg git-remote-gcrypt python3 rg gh; do command -v $t >/dev/null && echo "ok $t" || echo "MISSING $t"; done
```

## Ask

Nothing, unless something is missing. Then list each missing tool with one sentence on why:

| Tool | Why |
| --- | --- |
| `git` | the ICM is a git repo; history is the change journal |
| `gpg` | makes and holds the encryption key |
| `git-remote-gcrypt` | encrypts everything at push, so the host stores only a blob |
| `python3` | the commit checks and the page builders |
| `rg` | how the agent searches the ICM before it answers |
| `gh` | creates the private repo and logs in through the browser; only needed in step 06 |

Node is **not** needed to use an ICM.

## Do

Install only on their word, idempotently (`brew list x || brew install x`; on Linux the distro's
package manager; on Windows `winget install Git.Git`, which brings git and gpg, and copy
`git-remote-gcrypt` into a folder on PATH). On a Mac without Homebrew, stop and send them to
https://brew.sh: installing it asks for their password, which is theirs to type.

Then make the passphrase prompt work, or signing will hang later:

```bash
mkdir -p ~/.gnupg && chmod 700 ~/.gnupg
grep -q pinentry-program ~/.gnupg/gpg-agent.conf 2>/dev/null || echo "pinentry-program $(command -v pinentry-mac || command -v pinentry)" >> ~/.gnupg/gpg-agent.conf
grep -q GPG_TTY ~/.zshrc 2>/dev/null || echo 'export GPG_TTY=$(tty)' >> ~/.zshrc   # or ~/.bashrc
gpgconf --kill gpg-agent
```

## Checkpoint

The list of what will be installed, before installing.

## Proof

The Detect loop prints no `MISSING` line (`gh` may be missing if the owner will create the remote repo by hand).
