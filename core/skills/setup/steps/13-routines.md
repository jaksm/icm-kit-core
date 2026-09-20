# 13 Routines (optional)

Work that happens on a schedule, without the owner asking.

## Detect

`domains/system/output/connectors-and-routines.md` lists at least one routine with its schedule,
and the ICM holds a record that routine wrote.

## Ask

Propose one routine that follows from what they installed (with `morning-review`: the morning
review) and at most one that follows from their three-month goal. Every routine goes through
three gates, in order, each with their yes:

1. the signal and where it comes from
2. a sample of the real output, made now, by hand
3. switching it on

## Do

A routine is built the same way every time:

- **The prompt is one line** that points at a `SKILL.md`: "Do the morning review per
  core/workflows/morning-review/SKILL.md". The procedure lives in the ICM, so it can change
  without touching the scheduler.
- **Availability gate first.** If the ICM could not be opened, the routine stops and touches nothing,
  because its rules are read from the ICM.
- **The last thing it writes is a section on its own phases**, one line per phase, done or failed
  with the reason. A routine can die after its first output, and nothing else shows that.
- **It writes even when there is nothing to say.** An empty record proves the routine ran; an old
  record proves nothing.
- It alerts only on a meaningful change, and never between 22:00 and 08:00 local time.

How a routine is scheduled is the adapter's: `core/adapters/<harness>/SKILL.md`, capability
"schedule a routine". A harness without one: `recipes/any-routine.md`.

Then **run it once, now**, by hand, so the owner sees the result today and not tomorrow morning.

## Checkpoint

The three gates, and creating the schedule at the provider.

## Writes

`domains/system/output/connectors-and-routines.md`: per routine the schedule, what it reads, what it
writes, and how the owner knows it ran.

## Proof

The record the routine wrote exists, is dated today, and ends with the section on its phases.
