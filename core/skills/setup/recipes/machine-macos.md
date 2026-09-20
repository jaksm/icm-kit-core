---
trust_tier: verified
verified_on: 2026-09-20, macOS, run by the maintainers in a simulated setup (detection and gpg agent configuration; installation through Homebrew is long standing practice on the machine it was run on)
---

# The machine: macOS

```bash
command -v brew >/dev/null || echo "Homebrew is missing: https://brew.sh (the owner installs it; it asks for their password)"
for p in git gnupg git-remote-gcrypt pinentry-mac ripgrep gh; do brew list "$p" >/dev/null 2>&1 || brew install "$p"; done
```

Then the passphrase window and the socket length check from step 02. `python3` comes with the
command line tools; if `python3 --version` opens an install dialog, the owner confirms it.
