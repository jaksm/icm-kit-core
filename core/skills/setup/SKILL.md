---
name: setup
description: Stand up an ICM for one person, from an empty template to a working system, or adopt an ICM that already exists. Use when the owner pastes the setup prompt, says "run setup" or "continue setup", or when _config/setup.json has a pending step.
---

# Setup

Takes a person from nothing to an ICM that knows them, is encrypted, is backed up, opens on their
phone, and has run its first routine. It spans several sessions, so it keeps its state in a file
and picks up where it stopped.

## Inputs

- `_config/setup.json`, if it exists: where setup stands. No file means a first run.
- `how-we-talk.md`: once step 01 is done, how much to explain and in what manner. Obey it in every later step.
- `core/adapters/<harness>/SKILL.md`: exactly one, the harness you are running in. It says how each
  capability the steps name is done here. A capability it lacks is recorded as missing, with the
  manual fallback, never faked.
- `steps/NN-*.md`: read a step only when you reach it.
- A release of `icm-kit-core`, when a step says `<release>`: clone https://github.com/jaksm/icm-kit-core
  into a temporary folder outside the ICM.
- `references/explain-*.md`: material to explain from. Not text to paste: build the explanation in
  the owner's manner.

## Process

1. Read `_config/setup.json`. Missing: create it from the shape below with every step `pending`.
2. **After a core update, look again.** A step left `pending` with the evidence "not in this release"
   is checked against `steps/`: if its file exists now, it is an ordinary pending step.
3. **Adopt before you build.** For every step not `done`, run its **Detect** first. If the thing
   already stands (an ICM that predates the kit, a half finished earlier run), write `done` with the
   evidence and move on. Never redo what works.
4. Take the first `pending` step, read its file, do it. Each step file has the same parts:
   **Detect**, **Ask**, **Do**, **Checkpoint**, **Writes**, **Proof**.
5. A step is `done` only when its **Proof** gave the expected result, and that result is what goes
   in `evidence`. "I ran it" is not evidence. When everything is set up but the proof has to come
   from the world (a message that has not arrived yet), the state is `waiting`: on resume, only ask
   for the proof, do not start the step again. Evidence describes what **is**, not what is absent
   ("the page exists", never "no workflows installed"), or a later step makes it false.
6. The owner may skip any step marked optional. Write `skipped` with their reason; it goes to
   `domains/system/output/open-tasks.md` so it is not forgotten.
7. Commit after every step, message in the owner's language. The owner's own repo only exists from
   step 03, so 01 and 02 get their commits right after it. Then say in one or two sentences what
   now exists and what comes next, and ask whether to go on now or another day.
8. After the last step, run `steps/14-audit.md` even if some steps were skipped. Run it again after
   any later setup session; its evidence is overwritten, not appended.

### Checkpoints that hold in every step

- Passphrases, logins, CAPTCHAs and anything typed into a website are the owner's. Say what to do
  and wait. Never ask for a passphrase in the conversation, never write one to a file.
- Anything that leaves the machine (creating a remote repo, a cloud environment, a mail filter, a
  scheduled routine) happens on the owner's explicit word, one action at a time.
- Installing software: list what is missing and why each thing is needed, then install on their word.
- Verify where the result shows, not where the tool reports. A closed dialog is not confirmation.
- What the owner says they never want (lists, praise, long answers) holds from your very next
  message, not from the moment it is written to a file.
- The owner hears about their ICM, not about your tooling. Unavailable connectors, plugin notices
  and other status of the harness that setup does not need stay out of the conversation.

### Order

| # | Step | Optional |
| --- | --- | --- |
| 01 | questionnaire | no |
| 02 | machine | no |
| 03 | repo | no |
| 04 | who | no |
| 05 | key | no |
| 06 | remote | no |
| 07 | backup | recommended; may be skipped with a reason |
| 08 | cloud | yes |
| 09 | sources | yes |
| 10 | reminders | yes |
| 11 | workflows | yes |
| 12 | import | yes |
| 13 | routines | yes |
| 14 | audit | no |

A step whose file does not exist in this release is left `pending` with `"evidence": "not in this release"`.

## Outputs

- `_config/setup.json`, the canonical source of where setup stands:

```json
{
  "harness": "", "language": "", "os": "", "phone": "",
  "adopted": "",
  "explain": {"how_much": "", "manner": ""},
  "steps": {"01-questionnaire": {"state": "pending | waiting | done | skipped", "date": "", "evidence": ""}}
}
```

`adopted` is set when the ICM predates the kit: its steps were detected, not performed.

- The three personal records filled in the owner's words, their `<!-- setup: -->` notes deleted.
- One commit per step.
- What was skipped or is waiting on the owner, in `domains/system/output/open-tasks.md`.
- A closing message from step 14, in the owner's tone.
