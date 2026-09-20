---
trust_tier: unverified
---

# Any reminder channel

**What the capability must provide:** the agent can create one item with a title and a note in a
list the owner already looks at daily, from wherever the agent runs (their computer, a cloud
session, or both), and the item reaches their phone without them doing anything.

**What to find out:** does the app sync through an account or only live on one device; is there a
connector in the harness, an API, a command line, or an email-in address (many to-do apps turn a
mail to a private address into a task, and the ICM already treats mail as the hub); what a token
would be allowed to do.

**Order of preference:** a connector the harness already has; email-in; a calendar event; an API
with a token kept in the harness's secret storage; a local script. Never a script that drives a window.

**Proof:** the test item shows on the owner's phone, and they say so.

**When to say no:** if the only way in is a token with full account access, or automation of a
window. Then the channel is the calendar, or simply a section "next moves" at the top of
`open-tasks.md` that the agent reads out at the start of a conversation. Say it plainly.
