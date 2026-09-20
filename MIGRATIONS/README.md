# Migrations

One file per release that changes what an installed repo must do: `<from>-<to>.md`, for example
`0.1.0-0.2.0.md`. A release that only fixes code inside `core/` needs none.

A migration is written for the agent that will run it on a repo it has never seen, with the
owner's customizations in the way. It has four parts:

1. **What changed and why**, in two sentences.
2. **Moved or renamed**, as a table of old path, new path.
3. **Outside core/**: every change the owner's repo needs (hook paths, config keys, templates), each
   with a command or a before and after.
4. **Verify**: commands whose output proves the repo works again.

`pre-kit-0.1.0.md` is the migration of the repo this kit grew out of. It is the worked example of
moving an existing ICM onto core.
