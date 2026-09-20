# 12 Import (optional)

Bring in what is still alive from the systems the owner used before.

## Detect

`grep -c '^module import' core.lock` prints `1`, and `git log` holds at least one commit of an import group.

## Ask

Explain the trade first, not the technique. An ICM that knows them well personalizes better, and
the price is private material gathered in one place. And: old sources were written before this
system existed and are almost always stale. The aim is not to move everything. It is to pull out
what is still in use, and only they know what that is.

Then: where things live today (a notes app, another assistant's memory, an old repo, a disk, a big
mailbox), and which one hurts most to not have at hand.

## Do

`<release>/install.sh . --add import`, then `core/workflows/import/setup.md`. Add a row for
`core/workflows/import/` to the procedures table of the instruction file. One source at a time.

## Checkpoint

Before opening anything personal, ask. Nothing is written before they have answered the group's
table. A secret found in a source is never copied: report it so they can revoke it.

## Writes

Records in the areas, `domains/system/output/open-tasks.md` for what is left of the source.

## Proof

The first group of five is through: one commit whose message says what was skipped and why, and
`git status` is clean. An import of a large source goes on over many sessions; the step is `done`
after the first group, and the rest is a row in `open-tasks.md`.
