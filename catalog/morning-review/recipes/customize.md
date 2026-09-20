---
trust_tier: unverified
---

# Fitting the morning review to one owner

Most fitting is configuration, not code: labels that mean "needs me", the language, the questions.
Change `_config/morning-review.json` first.

For more, the contract itself can be overridden: copy `SKILL.md` to
`_config/overrides/core/workflows/morning-review/SKILL.md`, change the copy, and point the routine's
one-line prompt at the copy. Worth it for: own sections in the record (a section per client, a
section for one project); a second mailbox with different rules; a weekly variant that reads the
week's records instead of the mailbox.

Do not change: inbox only; never send, delete or spam; an unknown sender stays; the phases section
last; a record even when empty. Those are what make it safe to run unattended.
