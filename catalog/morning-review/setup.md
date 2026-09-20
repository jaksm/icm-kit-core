# Setting up the morning review

Needs the adapter's **mail** capability for the owner's provider. Without it, say so and do not
install: the provider's own rules (workflow `sources`) still sort the mail. Needs `sources` first.

## Ask

What "needs me" means for them beyond the defaults; what time they first look at their phone;
whether there is something they want asked every day for a while (a measurement, a count), and until when.

## Writes

`_config/morning-review.json`:

```json
{
  "time": "07:30", "language": "en",
  "needs_owner_labels": ["State", "Money"],
  "questions": [{"ask": "...", "until": "the owner says it is over", "answer_goes_to": "domains/<area>/output/<record>.md"}]
}
```

## First run and proof

1. A **dry run** now, together. Read the record with them: is anything listed under "would have
   been filed" that they wanted to see? Fix `senders.csv`, repeat until it is right.
2. One real run by hand. Proof: the record is dated today and ends with the phases section, and the
   unread count in the inbox equals the number under "needs you".
3. Only then schedule it: setup step 13, prompt "Do the morning review per core/workflows/morning-review/SKILL.md".
