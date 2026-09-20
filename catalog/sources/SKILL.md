---
name: sources
description: Add, check and retire the outside sources of an ICM (newsletters, feeds, notices from services), with mail as the hub and the provider's own rules doing the sorting. Use when the owner wants to follow something, when mail is being mis-sorted, or when a source has gone quiet.
---

# Sources

## Inputs

- `_config/sources/senders.csv`: the canonical list of who is sorted where. Columns: sender, label, keep_in_inbox, why.
- `domains/system/output/sources.md`: one row per source with the reason it is there.
- The recipe for the owner's mail provider in `recipes/`, or `recipes/any-mail.md`.

## Process

1. **Can the service send mail?** Before building anything for a new source, ask that. If yes, it
   is configured on its side to mail the owner, and that is the whole integration.
2. **Split by role, not by source.** What is addressed to the person (a deadline, money, a human,
   the state) comes by mail. Bulk signal (news, releases, videos) is better read as a feed by a
   script, because turning a feed into mail destroys its ids and dates, and with them deduplication.
   `recipes/rss-to-mail.md` is for the few feeds worth a mail each.
3. **Check a feed before trusting it**: `python3 core/workflows/sources/scripts/check-feed.py <url>`.
   The verdict comes from the body, never from the HTTP code.
4. **Read the existing rules at the provider first.** A rule that deletes beats a rule that labels,
   silently; two old delete rules once ate senders that had just been added as sources.
5. **Checkpoint.** Propose the row for `senders.csv` and the rule it becomes. The owner says yes.
6. Write the row, rebuild the rules the way the provider's recipe says, import or create them, then
   **open the list of rules and count**. A closed dialog is not confirmation.
7. A rule never touches mail that already arrived: relabel old mail with the same query, by hand, if it matters.
8. One source, then a few days of watching where its mail lands, then the next.

Retiring a source: unsubscribe (ask first: a sender that looks like noise may be a deliberate
signal), delete its row, rebuild. The reason goes in the commit message, not in a struck-through row.

## Outputs

`_config/sources/senders.csv`, the provider's rule file next to it when there is one,
`domains/system/output/sources.md`.
