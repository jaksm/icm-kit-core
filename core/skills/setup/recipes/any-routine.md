---
trust_tier: unverified
---

# A routine without a scheduler in the harness

**What the capability must provide:** at a set time, an agent session starts with the ICM opened
and unlocked, runs one line of prompt, commits, pushes, and ends, with nobody present.

**On a computer that is on at that time:** the system scheduler (`launchd` on a Mac, `cron` on
Linux, Task Scheduler on Windows) starts the harness in its non-interactive mode with the one-line
prompt, in the ICM folder. Things that bite: the scheduler's environment has no `GPG_TTY` and no
window for a passphrase, so the key must already be unlocked in the agent (`gpg-agent` cache time) or
the routine cannot push, and it should then commit locally and say so in its phases section; the
computer may be asleep (on a Mac, `pmset repeat wake`); the harness's permission mode must allow
what the routine does without asking, and nothing more.

**Proof:** the record of a scheduled run, dated by the scheduler and not by hand, with its phases section.

**When to say no:** if the computer is rarely on at a fixed time. Then there are no routines, the
owner runs the skill by saying its name when they sit down, and that is a fine way to live.
