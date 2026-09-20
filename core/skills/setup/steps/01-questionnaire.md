# 01 Questionnaire

Learn enough to talk to this person properly for the rest of setup. Short: six questions, one at a
time, in the language they wrote to you in. Do not explain the system yet.

## Detect

`_config/setup.json` has `language`, `os` and both `explain` fields, and `how-we-talk.md` has no
`<!-- setup: -->` note about register left. In an ICM that predates the kit, read `how-we-talk.md`
(or its equivalent named in the instruction file) and fill the fields from it instead of asking.

## Ask

1. What should this help you with in the next three months? (their words go to step 04)
2. Which computer and which phone do you use?
3. Have you used git before? Encryption keys? A terminal? (three yes/no, no judgement)
4. **How much** do you want explained as we go:
   - just do it and tell me what was done
   - explain each step before you do it
   - teach me, so I could do it myself next time
5. **In what manner** do explanations land best for you:
   - a comparison from everyday life
   - show me the command, then say what it did
   - why first, how second
   - small steps, and check with me after each
6. Is there something a past assistant did that annoyed you?

## Do

Pick the harness from the environment you run in; do not ask. Mirror their register from their
answers: length, formality, mixed languages.

## Writes

- `_config/setup.json`: `harness`, `language`, `os`, `phone`, `explain.how_much`, `explain.manner`.
- `how-we-talk.md`: language and register, the two explanation choices in their own words, the
  answer to 6 under what is never done. Leave the other setup notes for step 04.

## Proof

`grep -c '"how_much": ""' _config/setup.json` prints `0`.
