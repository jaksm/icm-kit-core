# Material: git, as much as an ICM owner needs

- A repo is a folder that remembers every version of every file. A commit is one remembered moment, with a message saying why.
- The ICM has no separate change journal: `git log` is the journal. That is why commit messages here
  are full sentences about what was learned and what changed.
- `push` sends new commits to the host, `pull` brings the ones made elsewhere (the phone). Always
  pull before pushing: an encrypted push overwrites what is there.
- There is one branch, `main`. Branches and pull requests need a host that can read files; this one cannot.
- A conflict means the same record changed in two places. The agent shows both versions and asks which is right.
- The hook in `.githooks/` runs three checks before every commit (dead links, style rules, secrets)
  and refuses the commit if one fails. A refusal is the system working.

Comparisons that hold up: a notebook where every page keeps its earlier drafts underneath; track
changes that never gets turned off.
