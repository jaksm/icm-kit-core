---
trust_tier: unverified
---

# Fitting the feed to this owner

Read `core/RECIPES.md` first. Nothing here changes `core/`.

- **Words and language**: `labels` in `_config/feed.json`. Every key of `LABELS` in
  `build-feed-page.py` can be replaced; the library's own words are in `_config/labels.json`.
- **Link labels per site**: `hosts`, a regex of the host to the label. The label says what happens.
- **Numbers**: `max_age_hours`, the gaps and budgets, `seen_ms`, `video_seconds`. They are agreements.
  Change one when `<data>/diary.csv` or `manifest.json` shows a reason, and write the reason and the
  date into the owner's record of feed preferences.
- **Another look**: copy `template/feed-template.html` to
  `_config/overrides/core/workflows/feed/template/feed-template.html` and edit the copy. The build
  refuses a template that lost one of the rules or script lines it depends on (`HOLDS` in the
  builder); keep them, each is there because its absence once broke the page silently.
- **A row of a kind that is only theirs** (listings, a price they track, a game's patch notes): it
  is content, not code. Write a skill in the owner's `skills/` that produces stories for that row
  from its own source, and let this workflow place them.
- **A card that does something** (`actions`): add the action to `_config/actions.json` first. The
  agent cannot compose a call on a card; the build refuses an id that is not in the catalog.

Proof after any change: `build-feed-page.py --check`, then `--preview` at phone width.
