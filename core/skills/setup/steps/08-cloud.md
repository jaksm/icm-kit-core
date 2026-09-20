# 08 Cloud (optional)

The ICM opens from the phone with the computer off.

## Detect

The adapter's `SKILL.md` says how to tell. Usually: a second key is listed in
`git config remote.origin.gcrypt-participants`, and the owner can name the environment.

## Ask

Whether they want it. What it costs: a second key that lives at the provider, limited to one year
and revocable on its own, so the main key never leaves the computer.

## Do

This step belongs to the adapter. Open `core/adapters/<harness>/SKILL.md`, section **Setup**, and
follow it with the owner. If the adapter has no cloud capability, write that down as missing, tell
them the ICM works from the computer only, and mark the step `skipped`.

Before changing any adapter file for this owner, read `core/adapters/<harness>/recipes/customize.md`.

## Checkpoint

Every action at the provider's site is theirs: creating the environment, pasting the setup script,
pasting the key into the environment's variables.

## Writes

`domains/system/output/connectors-and-routines.md`: environment name, the cloud key's fingerprint
and expiry. A reminder a week before it expires, through the channel from step 10 if it exists,
otherwise a line in `open-tasks.md`.

## Proof

A change asked for from the phone arrives on the computer: `git pull --rebase origin main` brings a
commit made in the cloud session.
