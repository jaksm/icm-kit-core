---
trust_tier: unverified
---

# The machine: Linux

Read `core/RECIPES.md` first: nobody has run this on a desktop. The cloud setup script in the
adapter installs `gnupg` and `git-remote-gcrypt` on Ubuntu 24.04 through apt, and that part is known to work.

Debian and Ubuntu: `sudo apt-get install -y git gnupg git-remote-gcrypt python3 ripgrep gh pinentry-gnome3`
(or `pinentry-qt`, `pinentry-curses` without a desktop). Fedora: `dnf`, the same names except
`gnupg2`. Arch: `pacman -S git gnupg python ripgrep github-cli`, and `git-remote-gcrypt` from the AUR.

`sudo` asks for the owner's password: they type it. Then the passphrase window from step 02, with
the shell rc file of their shell. Without a graphical session, `pinentry-curses` needs a real
terminal: `export GPG_TTY=$(tty)` matters more here than anywhere.

Proof: the Detect loop of step 02 prints no `MISSING` line.
