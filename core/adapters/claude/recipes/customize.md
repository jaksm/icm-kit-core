# Fitting the adapter to one owner

The adapter works as shipped. Change it only when the owner's situation needs it, and never inside
`core/`: an update replaces that folder whole.

## How an override works

Copy the file to `_config/overrides/<the same path>` and change the copy.

| File | Who looks at the override first |
| --- | --- |
| `core/adapters/claude/hooks/session-start.sh`, `stop-sync.sh` | `make-cloud-setup.sh`, when it embeds the hooks into the cloud setup script. Regenerate the script and paste it into the environment again; a cached container keeps the old one for about a week. |
| `core/adapters/claude/hooks/pre-push` | nobody automatically: `.githooks/pre-push` is a symlink the owner's repo owns. Repoint it to the copy. |

Record every override in `domains/system/output/connectors-and-routines.md` with the reason. When
core updates, `core-update` diffs each override against the new release of the file it came from.

## When it is worth it

| Situation | Change |
| --- | --- |
| the owner does not want a commit after every reply | in `stop-sync.sh`, sync only when a marker file exists, and tell them how to set it |
| commit messages in the owner's language or style | the sentence `stop-sync.sh` gives the agent when it asks for a commit |
| extra tools a routine needs in the cloud | **not** in the hooks. Add them to the setup script section of the generator copy, and make the routine survive without them: a cached container predates the change |
| a second device that must not push | leave the adapter alone; give that device a key that is not a participant |

## Checkpoint

Show the owner the diff of the copy against the original before it is used. A hook runs on every
session with their key unlocked.
