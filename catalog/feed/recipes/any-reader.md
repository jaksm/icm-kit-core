---
trust_tier: unverified
---

# A source the readers do not know, and facts about hosts that rot

Read `core/RECIPES.md` first.

`read-sources.py` knows four kinds of address: a video site's transcript, a forum thread as JSON, a
link aggregator's thread as RSS, and an article through text extraction. The numbers it carries
(one anonymous request a minute, a daily ceiling per IP, a breaker after three blocks) were
**measured on 2026-09-19 from one network**. Treat each as a claim with a date.

**When `manifest.json` shows a reader failing** (`fallback_reason` or `unread_by_reason` grows):

1. Make one request by hand and read the status and the rate headers. Is it the host refusing
   (403, a bot wall), a limit (429, a reset time), or the library (an exception name)?
2. A limit: raise the gap or lower the budget in `_config/feed.json`. A bot wall: no retry helps,
   the feed summary is the honest ceiling, leave it. A changed endpoint: write the owner's reader.
3. Write what was measured, with the date, into the owner's record of the funnel.

**A new kind of source** (a podcast with transcripts, a store's price page, an API with a key): the
owner's own reader is a script in their `skills/<name>/scripts/` that takes the day's
`02-passed.jsonl` rows of that host and appends rows to `025-read.jsonl` with the same keys:
`text`, `text_source`, `failed_reason`, `kind`. Same rules: a reason on every row not read, a
fallback never hides the failure, a missing library skips the item and never kills the run, no key
or token in the script or the ICM. A source with no feed at all: `core/workflows/sources/recipes/`.

Proof: a run where the manifest's counts for the new kind equal the rows in the two files.
