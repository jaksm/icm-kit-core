---
name: morning-review
description: A daily routine that goes through the inbox, files everything that does not need the owner, leaves unread only what does, and writes a dated record with proof that it ran. Use as a scheduled routine, or when the owner says "do the morning review" or asks what came in.
---

# Morning review

The owner's rule this serves: **unread in the inbox means it needs me.** Nothing else stays there.

## Inputs

- Availability: if the session could not open the ICM, **stop**. Nothing in the mailbox is touched
  while the ICM is closed, because the sorting rules are read from it.
- The mailbox, inbox only, through the adapter's mail capability: read, label, mark read, archive.
  Never send, never delete, never mark as spam.
- `_config/sources/senders.csv`: who is filed where, and who stays in the inbox.
- `_config/morning-review.json`: see `setup.md`.
- Yesterday's record in the folder `records` names (default `domains/system/data/morning-review/`), so nothing is reported twice.

## Process

1. **Sort.**
   - *Needs the owner* (a reply, a decision, a deadline, money, the state, a person writing to
     them): stays in the inbox, stays unread. It may get its label, it does not leave.
   - *Everything else* (news, feeds, notifications, receipts): label by `senders.csv`, mark read,
     remove from the inbox. Archiving is taking the inbox label off; it is never deleting.
   - *Left yesterday, opened since*: a message in the inbox the owner has already read goes to its
     label and leaves. This overrides `keep_in_inbox`.
2. **An unknown sender is not filed.** It stays in the inbox, and the record says its place is not
   known and proposes a label. Quietly filing into the wrong label is worse than one message too many
   in the inbox, because nobody sees it happen. When unsure whether something needs the owner, it
   stays: a miss on that side costs a glance, on the other a missed deadline.
3. **Write the record** `<records>/<date>.md`, frontmatter
   `type: Tracking`, `status: active`, `trust_tier: machine-confirmed`, first line "N messages, M
   need you". Sections, in the owner's language:
   - needs you: every item, with why
   - signals: what touches something that is open in the ICM, with the path it touches
   - news: grouped by topic, one line each; news is not retold
   - could go into the ICM: proposals with the path; written only when the owner says so
   - senders without a place: each stays in the inbox, with a proposed label
   - filed: one line per label with a count
   - questions this routine is asking (from the config), each until its end condition
4. Money appears as a fact and an aggregate ("a statement arrived"), never as amounts per transaction.
5. **Last of all, write the section on the routine's own phases**, one line per phase: `sort ok`,
   `record ok`, or `record failed: <reason>`. A routine can die after its first output, and nothing else shows it.
6. Commit with a one-line message. The adapter pushes.

**Write the record even when nothing came in.** An empty record proves the routine ran; an old record proves nothing.

**Dry run**: when asked for a dry run, do everything except step 1's changes to the mailbox. The
record says at the top that it was a dry run and lists what *would* have been filed. This is how the
routine is tried on a real mailbox before it is trusted with it.

When the owner answers the review ("archive the second one, the third goes to the accountant's
label"), apply it at once by the same rules, and add a row to `senders.csv` if a sender's place is now known.

## Outputs

The dated record; label changes in the mailbox; new rows in `senders.csv`.
