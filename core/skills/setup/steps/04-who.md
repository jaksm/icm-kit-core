# 04 Who

The three personal records and the first areas. This is the step that makes it their ICM, so it is
a conversation, not a form.

## Detect

`grep -l '<!-- setup:' *.md` at the root of the ICM prints nothing (that covers the three records
and the instruction file, whatever the adapter calls it).

## Ask

Every record carries a `<!-- setup: -->` note saying what to collect and how to ask. Follow the
notes. One question at a time, their words written down, not a summary of them.

If they have earlier material about themselves (an older assistant's memory export, a notes app, a
CV), do not start from questions:

1. Read it all first. Merge what repeats; keep the earliest date a thing was said.
2. Separate what is undisputed from what conflicts or looks stale.
3. Turn the conflicts into a short numbered list of questions, one per dispute.
4. Ask them in rounds of about four. Their answer is `authoritative` and overrides every source.
5. What they cannot answer stays visibly open in `domains/system/output/open-tasks.md`. Never resolve it by inference.

Areas: from question 1 of the questionnaire, propose two to four areas. An area earns a folder
only when it will hold at least three records or one table; the rest waits in `memory.md`.

## Do

Copy `domains/_example/` once per agreed area, fill its `CONTEXT.md`, add its routing row to the
instruction file in **their words for the topic**, translate the trigger words table, replace the
title and the opening note of the instruction file. Delete `_example` when a real area exists.

## Checkpoint

Before the first commit of each record, show them the page and ask whether it is them. Anything
about other people: first names and roles only, and ask before writing more.

## Writes

`who-am-i.md` and `how-we-talk.md` with `status: active` once they agreed; `memory.md` stays
empty unless they said "remember"; `domains/<area>/`; the instruction file. One commit per round.

## Proof

The Detect grep prints nothing, and `./core/scripts/link-check.sh` ends with `0 dangling links`.
