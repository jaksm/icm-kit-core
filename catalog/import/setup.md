# Setting up import

## Ask

Which sources exist, and which one first. How much time they want to give it per sitting: a group of
five takes a few minutes of their attention, and a tired owner says "skip" to everything.

## Do

Pick the recipe for the first source. Make the inventory (titles only). Create `archive/` at the
root if they want anything kept as is, and put `archive` in `_config/graph.json` so the graph draws
it in grey, and in the hook's `LINK_CHECK_SKIP` and `STYLE_CHECK_SKIP`, because archived text is not theirs to fix.

## First run and proof

The first group of five, together. Proof: its commit exists and its message lists what was skipped.
