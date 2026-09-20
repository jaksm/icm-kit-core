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
G="${GNUPGHOME:-$HOME/.gnupg}"; mkdir -p "$G" && chmod 700 "$G"
grep -q pinentry-program "$G/gpg-agent.conf" 2>/dev/null || echo "pinentry-program $(command -v pinentry-mac || command -v pinentry)" >> "$G/gpg-agent.conf"
rc="$HOME/.$(basename "${SHELL:-zsh}")rc"; grep -q GPG_TTY "$rc" 2>/dev/null || echo 'export GPG_TTY=$(tty)' >> "$rc"
gpgconf --kill gpg-agent
printf %s "$G/S.gpg-agent" | wc -c      # must be under 100
```

That last number matters on a Mac: gpg talks to its agent through a socket in that folder, and the
system refuses a socket path longer than 104 characters. With a long home path key creation dies
with `can't connect to the gpg-agent: File name too long`, which no owner can interpret. If the
number is 100 or more, put a redirect file at `$G/S.gpg-agent` (and the same for
`S.gpg-agent.ssh`, `S.gpg-agent.extra`, `S.gpg-agent.browser`, `S.keyboxd`) holding two lines,
`%Assuan%` and `socket=/tmp/gpg-<user>/S.gpg-agent`, with that folder created mode 700. Keys stay where they are.

## Checkpoint

The list of what will be installed, before installing.

## Proof

The Detect loop prints no `MISSING` line (`gh` may be missing if the owner will create the remote repo by hand).
