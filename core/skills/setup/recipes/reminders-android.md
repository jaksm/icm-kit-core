---
trust_tier: unverified
---

# Reminders on an Android phone

Find out what they already use: Google Tasks, Google Keep, the Samsung Reminder app, TickTick,
Todoist. Then:

- **Google Tasks** lives inside the Google account, so it syncs to the phone by itself. The agent can
  reach it only if the harness has a connector that writes tasks; most have one for the calendar
  and none for Tasks. If not, use `reminders-calendar.md`: Google Calendar shows on the same phone.
- **Todoist, TickTick** and similar have an API and often a connector. Check the adapter's list of
  connectors first. An API token is a secret: it goes into the harness's own secret storage, never
  into the ICM and never into the conversation.
- **Samsung Reminder, Keep**: no way in from outside that is worth building. Use the calendar.

Two lists, as in step 10. Proof as in step 10: the owner sees the test item on the phone.
