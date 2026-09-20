---
trust_tier: unverified
---

# A large mailbox

Thousands of messages are volume, and volume is a script's job, not an agent's: an agent
transcribing them stalls partway and loses its work. Build, in the owner's `skills/`, a small
**read-only** script (the narrowest scope the provider offers, technically unable to change
anything) that lists sender, subject, date and the unsubscribe header into a CSV outside the ICM.
Its credentials live outside the ICM too.

Then the agent judges from the CSV: senders by count, what is a source worth keeping (workflow
`sources`), what holds facts worth a record, what to unsubscribe from. Count messages, not
threads. Nothing is archived or deleted before the owner has read the log of what would be.
