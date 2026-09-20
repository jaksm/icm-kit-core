---
name: expenses
description: Spending per month and category, from the owner's bank statements to an aggregate, an answer and a page, with only aggregates ever leaving the data files. Use when the owner asks what was spent, how a month stands against the plan, or wants a new statement imported.
---

# Expenses

## Inputs

- `_config/expenses.json`: the data folder, currency, plan, income and goal if the owner wants them
  shown, which categories count as opaque, names of categories and months, labels.
- `_config/expenses/categories.csv`: pattern, category.
- `<data>/transactions.csv`, written by **the owner's own parser**, built from
  `recipes/statement-parser.md` and living in their `skills/`; and `<data>/monthly.csv`.

## Process

1. **Answers and records carry aggregates only**: a month, a category, a ratio to the plan. Never a
   single transaction, never a name next to an amount, never what one person owes. Read
   `monthly.csv` to answer; open `transactions.csv` only to fix a category, and show only the rows asked for.
2. **Checkpoint: nothing is imported, deleted or recategorized without the owner's word.** The
   parser extracts; categories are proposed after they have looked.
3. A new statement: run their parser, then `scripts/categorize.py`, then `scripts/aggregate.py`.
   `aggregate.py` refuses a statement that does not reconcile; that is the parser's bug, fix it there.
4. Look at the share of `other` that `categorize.py` prints. Propose a new pattern only for a
   description that really occurs, and let the rest stay `other`.
5. After any change, **read the state back** before saying "imported": row count, months, the last date.
6. The page: `scripts/build-expenses-page.py`, published the way the adapter says, as a private
   page, always to its existing address.
7. A statement is never printed whole into the conversation.

## Outputs

`transactions.csv`, `monthly.csv`, the page, and `<money area>/output/expenses-state.md`: which statements are in, how many rows, the last date.
