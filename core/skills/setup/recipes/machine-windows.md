---
trust_tier: unverified
---

# The machine: Windows

Read `core/RECIPES.md` first: nobody has run this.

The plan, in order:

1. **Git for Windows** brings `git`, `gpg` and Git Bash in one install: `winget install --id Git.Git -e`.
   Everything in this kit that is a `.sh` file runs in **Git Bash**, not in PowerShell or cmd. Say
   that to the owner once, and open Git Bash for every later step.
2. `gpg` lives inside the Git install (`<Git>\usr\bin\gpg.exe`), and Git Bash finds it. If the owner
   also has Gpg4win, there are now two keyrings; pick one and use it everywhere, or keys made in
   one will be invisible in the other. Verify with `gpg --version` and `gpg --list-secret-keys` in Git Bash.
3. **git-remote-gcrypt** is a single shell script. Download it from its repository, put it in
   `~/bin/` inside Git Bash, `chmod +x`, and check `command -v git-remote-gcrypt`. `~/bin` is on
   PATH in Git Bash only if it exists when the shell starts: open a new one.
4. `python3`: `winget install --id Python.Python.3.12 -e`. On Windows the command is often `python`
   or `py`, not `python3`. The hook and the builders call `python3`; if it is missing, make a small
   `~/bin/python3` script that runs `python "$@"`, and verify with `python3 --version` in Git Bash.
5. `rg`: `winget install --id BurntSushi.ripgrep.MSVC -e`. `gh`: `winget install --id GitHub.cli -e`.
6. The passphrase window: Git's gpg uses its own pinentry and needs no configuration. If key
   creation hangs, that is the first place to look.
7. Line endings: `git config --global core.autocrlf false` before cloning, or the hook scripts
   arrive with CRLF and fail with `bad interpreter`.

Proof: the Detect loop of step 02, run in Git Bash, prints no `MISSING` line; and
`git commit --allow-empty -m test` in the ICM shows the three checks running.

Known unknowns, to watch for and report: symlinks (`.githooks/pre-push` is one; Git for Windows
needs Developer Mode or `core.symlinks true` to create it, otherwise it arrives as a text file
holding the path, and the push guard silently does not run; if so, replace it with a copy of the
hook), and long paths (`git config --global core.longpaths true`).
