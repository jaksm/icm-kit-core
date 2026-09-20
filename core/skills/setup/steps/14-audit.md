# 14 Audit

Prove the system works, from the files, not from memory of having done the steps.

## Detect

Never skipped, never adopted. Run it at the end of every setup, including a partial one.

## Do

1. **Every `done` step again.** Run each step's **Detect and its Proof**, and test every claim its
   `evidence` makes: a Detect is the cheap question, and the thing that broke is usually something
   only the evidence mentions (a hook file that is gone, a page that no longer builds). Compare with
   `_config/setup.json`. A step that no longer proves itself: fix it now and it stays `done` with new evidence that
   says what was broken; if you cannot fix it, it goes back to `pending` and into `open-tasks.md`.
   A `done` step without evidence gets its evidence from its Proof, or is treated the same way.
   Evidence that is merely out of date on a step that still proves itself is rewritten, not appended to.
   **Pending and skipped steps**: look once whether a core update changed them (a step file that now
   exists, a Detect that now passes) and correct the entry; adopting it is the next "continue setup". A check that **this environment** cannot run (no key in a cloud session, no gpg) is recorded
   as "not re-proven here" and the step keeps its state: that is about the session, not the ICM.
2. **The repo checks**, the way the hook runs them: commit this step's own changes and read the
   hook's lines (a check that prints nothing, like the leak check, passed). `ls .githooks/` shows
   `pre-commit` and the adapter's push guard.
3. **The shape of the ICM**, because everything in the instruction file is paid for in every session:

```bash
wc -l <instruction file>                          # the adapter names it: under 200 lines
cat <instruction file> who-am-i.md how-we-talk.md | wc -c   # under 40000 bytes
find domains -name CONTEXT.md | wc -l; find domains -name '*.md' | wc -l
```
   A number over the limit is a finding for the owner, not a failure.
4. **Nothing waits on one machine**, checked **last**, after this step's commit: pull with rebase,
   push, then `git log origin/main..main --oneline | wc -l` prints `0`. If the push cannot happen
   here, the owner hears the number and why, and it goes to `open-tasks.md`.
5. **Nothing personal left in the open**: `git remote -v` shows only the `gcrypt::` remote (in a
   cloud session the adapter may add a plain one with push disabled), and `git status` is clean.
6. **Resume works**: `_config/setup.json` has no step `done` without evidence.

Fix what you can. What needs the owner goes to `domains/system/output/open-tasks.md`.

## Writes

`_config/setup.json` step 14 with the evidence, `open-tasks.md`.

## Proof and closing

Tell them, in their tone and language from `how-we-talk.md`, in a few sentences: that all systems
are operational **if that is true**, and otherwise exactly what is not and what happens next; what
exists now, what you repaired, what was skipped and is waiting, and the one thing to try first.
Never say it works when something could not be proven here.
Not a report. The kind of message they would send a friend who just finished helping them move in.
