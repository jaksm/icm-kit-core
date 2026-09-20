---
trust_tier: verified
verified_on: 2026-09, a feed-to-mail service, by the first owner of an ICM (then partly abandoned, see below)
---

# A feed as mail

For a source that has a feed and cannot send mail itself. A feed-to-mail service takes the feed URL
and an address, sends a confirmation mail, and from then on every new item arrives as a message
that a rule files under one label.

Mind the direction. Services exist for both ways, and the one that turns **mail into a feed** is the
opposite of what is wanted here and looks the same in a search result.

Why this is only for a few feeds: the conversion destroys the item's id, date, author and category,
so deduplication and parsing stop working. One owner moved about a hundred feeds from mail back to
a script that reads feeds directly, and kept mail for what is addressed to a person. Use this for the
handful of feeds where each item deserves to be seen as a message.

Check the feed first with `core/scripts/check-feed.py`. A feed returns its whole window on every read,
so a new subscription may deliver a burst of old items on day one.
