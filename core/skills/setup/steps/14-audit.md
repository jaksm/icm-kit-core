# 14 Audit

Prove the system works, from the files, not from memory of having done the steps.

## Detect

Never skipped, never adopted. Run it at the end of every setup, including a partial one.

## Do

1. **Every `done` step again.** Run each step's **Detect** and compare with the `evidence` in
   `_config/setup.json`. A step that no longer proves itself goes back to `pending`, and you fix it
   now. A check that **this environment** cannot run (no key in a cloud session, no gpg) is recorded
   as "not re-proven here" and the step keeps its state: that is about the session, not the ICM.
2. **The repo checks**: `./core/scripts/link-check.sh`, `./core/scripts/style-check.sh`, and a commit to see the hook run.
3. **The shape of the ICM**, because everything in the instruction file is paid for in every session:

```bash
wc -l <instruction file>                          # the adapter names it: under 200 lines
cat who-am-i.md how-we-talk.md | wc -c            # with the instruction file: under 40000 bytes
find domains -name CONTEXT.md | wc -l; find domains -name '*.md' | wc -l
```
   A number over the limit is a finding for the owner, not a failure.
4. **Nothing waits on one machine**: `git log origin/main..main --oneline | wc -l` prints `0`, or the
   owner hears how many commits exist only here.
5. **Nothing personal left in the open**: `git remote -v` shows only the `gcrypt::` remote (in a
   cloud session the adapter may add a plain one with push disabled), and `git status` is clean.
6. **Resume works**: `_config/setup.json` has no step `done` without evidence.

Fix what you can. What needs the owner goes to `domains/system/output/open-tasks.md`.

## Writes

`_config/setup.json` step 14 with the evidence, `open-tasks.md`.

## Proof and closing

Tell them, in their tone and language from `how-we-talk.md`, in a few sentences: that all systems
are operational, what exists now, what was skipped and is waiting, and the one thing to try first.
Not a report. The kind of message they would send a friend who just finished helping them move in.
