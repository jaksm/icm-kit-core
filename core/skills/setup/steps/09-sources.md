# 09 Sources (optional)

What reaches the ICM from outside, without a connector per service.

## Detect

`domains/system/output/sources.md` lists at least one source with its reason, and the workflow is
installed: `grep -c '^module sources' core.lock` prints `1`.

## Ask

Explain the one idea first: **mail is the hub**. Almost every service can send an email, so
instead of wiring each service to the agent, each service is told to email, and one mail
connection covers all of them. Known senders are sorted by the mail provider's own rules at
arrival, not by the agent; the agent only reads what is left.

Then: which mail provider they use, and which two or three things they wish they did not miss
(a newsletter, a project's releases, a government notice, a shop's price alert).

## Do

`<release>/install.sh . --add sources`, then follow `core/workflows/sources/setup.md`. It picks the
recipe for their provider; for a provider without one, `recipes/any-mail.md`.

## Checkpoint

Anything created at the mail provider (a rule, a label, a folder) and every subscription is on the
owner's word. **Look at the rules that already exist before adding one**: a rule that deletes beats
a rule that labels, silently.

One source, then a pause of a few days. Being able to add thirty in five minutes is not a reason to.

## Writes

`_config/sources/senders.csv`, `domains/system/output/sources.md` (one row per source, with why it is there).

## Proof

A message from the new source arrived and landed where the rule says. Looked at in the mailbox, not assumed.
