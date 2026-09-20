# Setting up sources

## Ask

Which mail provider; whether labels or folders already exist (**use theirs**, never bring a scheme:
a planned new scheme was once thrown away for the nine labels already in the account); the two or
three things they do not want to miss.

## Do

1. Pick the recipe: `recipes/mail-gmail.md` (verified), `mail-outlook.md`, `mail-fastmail.md`,
   `mail-icloud.md`, `mail-proton.md` (unverified), or `any-mail.md`.
2. Read the rules that exist. Write them into `_config/sources/senders.csv` first, so the file
   describes reality before it changes it.
3. Add at most three sources, one at a time, per `SKILL.md`.
4. If the agent has no way to read this mailbox (no connector for the provider), say so now: the
   provider's rules still sort the mail by themselves, which is most of the value, but
   `morning-review` cannot be offered. Record that as a missing capability with its fallback.

## Writes

`_config/sources/senders.csv`, `domains/system/output/sources.md`.

## Proof

One message from a new source arrived where its rule says, seen in the mailbox.
