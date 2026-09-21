---
trust_tier: unverified
---

# An ICM the owner already has

The one source that is not stale: it is recent, it is the owner's own words, and it already has the shape (areas, records,
a memory file). So the groups of five do not apply. The unit is the **area**, and the owner decides per area, not per record.

1. Inventory with `find` and `git log --stat`, by area: name, number of records, date of the last change. Never by opening files.
2. Search for secrets twice, exactly as `source-old-repo-or-disk.md` says. A flagged file is not opened and not moved; it is
   reported as a path.
3. One table to the owner: area, records, last change, and a proposal (bring, leave). They answer once for the whole table.
4. A brought area is copied whole into `domains/<area>/`, keeping its files as they are. Then only what the new ICM checks by
   script is fixed: frontmatter the checks require, links that now dangle, names the style check refuses. Content is not rewritten.
5. The identity files (who the owner is, how you talk, memory) are **merged, not copied over**: setup has just written fresh
   ones with the owner, and those win where the two disagree. A disagreement is shown, not quietly fixed.
6. One commit per area, with the count of records in the message. The old ICM is left untouched; nothing is deleted from it.

Skills, hooks, scripts and config of the old ICM are not brought: the new one has its own from `core/`. If an old skill did
something the catalog does not, it is written down as one line in the open tasks, not ported on the spot.
