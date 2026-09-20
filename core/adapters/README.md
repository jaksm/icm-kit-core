# Adapters

Everything in `core/` works with any coding agent that can read files and run a shell, except what
is in this folder. An adapter is the part that depends on one harness.

Today there is one: `claude/`. `codex/` and `antigravity/` hold this contract and nothing else yet.

## What an adapter must provide

| Capability | What the rest of the system assumes | Claude |
| --- | --- | --- |
| Instruction file | One file at the repo root the agent reads first, which routes to everything else | `CLAUDE.md` |
| Sync after a reply | Changes are committed and pushed to the encrypted remote without the owner asking | `claude/hooks/stop-sync.sh` |
| Session start | The encrypted remote is unlocked and the plain one can not be pushed to | `claude/hooks/session-start.sh` |
| Push guard | A push that is not to the encrypted remote, or not to `main`, is refused | `claude/hooks/pre-push` |
| Cloud session | The repo can be opened with the owner's computer off, from a phone | `claude/scripts/make-cloud-setup.sh` |
| Revocation | A cloud key can be withdrawn and the repo re-encrypted | `claude/scripts/revoke-cloud-key.sh` |
| Routine | At a set time a session starts with the ICM open, runs a one-line prompt that points at a `SKILL.md`, commits and ends | cloud routines |
| Mail | Read the inbox, label, mark read, archive. Never send, never delete | the Gmail connector; other providers: none today |
| Calendar | Create and read events in a calendar the owner chose | the Google Calendar connector |
| Reminder | Create one item in a list the owner already looks at | none from a cloud session; on a Mac `core/scripts/remind.sh`; otherwise a calendar event |
| Publishing a page | A built HTML file becomes a private page with a stable URL | artifacts |
| Skills | A folder with `SKILL.md` is discoverable by name and description | `.claude/skills/`, `skills/` |

## Rules

- Nothing outside `core/adapters/` names a harness, a vendor or a model. A skill says "publish the
  page", the adapter's `SKILL.md` says how.
- An adapter ships its own `SKILL.md` with `name: icm-adapter-<harness>`; the onboarding skill
  loads exactly one.
- A capability the harness lacks is written down as missing, with the manual fallback, not faked.
