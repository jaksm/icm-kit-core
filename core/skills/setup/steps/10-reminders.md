# 10 Reminders (optional)

The way the ICM reaches the owner when they are not talking to it.

## Detect

`domains/system/output/connectors-and-routines.md` names a reminder channel, and `_config/reminders.json` exists.

## Ask

Which reminders or to-do app they already look at every day. **Use that one.** A channel they have
to learn to check is a channel they will not check. Then explain the rules, because the rules
matter more than the app:

- It is a channel, not a task database. The ICM holds the plan; the reminder holds the next move.
- Two lists: a catch-all, and "today". The agent only ever writes to the catch-all. What moves to
  "today" is the owner's decision, and only what can be finished that day belongs there: one
  impossible item makes the whole list unclearable.
- A thing with several steps goes into a record in its area as a chain. Only the first day-sized
  step becomes a reminder; when they say it is done, the next link follows.
- Writing a reminder is always cheap and always allowed after their yes. Deciding when is theirs.

## Do

| They use | How |
| --- | --- |
| Apple Reminders, and the agent runs on their Mac | ready: `core/scripts/remind.sh "title" "note"`; list name in `_config/reminders.json` |
| anything, and the agent must reach it from a cloud session | `recipes/reminders-calendar.md` |
| an Android phone | `recipes/reminders-android.md` |
| Windows, Microsoft To Do | `recipes/reminders-windows.md` |
| something else | `recipes/any-reminders.md` |

All recipes are unverified, and the ready script is too until this step has run it once: read `core/RECIPES.md`.

## Checkpoint

Creating the two lists (the owner does it, or says yes), and the first test reminder.

## Writes

`_config/reminders.json` (`{"channel": "...", "list": "..."}`), and the channel with its rules in
`domains/system/output/connectors-and-routines.md`.

## Proof

Create one reminder named "ICM test, delete me" and **ask the owner whether they see it on their
phone**. Their yes is the proof. Then they delete it.
