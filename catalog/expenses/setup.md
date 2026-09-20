# Setting up expenses

## Ask

Currency. Whether they want a monthly plan shown, and income and a savings goal (all optional: with
none of them the page shows spending alone). Which categories are "opaque" for them, such as cash
withdrawals: money whose real purpose the statement cannot show. Which bank, and whether it offers
a CSV or spreadsheet export; ask for that before a PDF.

## Writes

`_config/expenses.json` (every key optional; defaults in `scripts/common.py`):

```json
{
  "data": "domains/money/data", "currency": "EUR", "out": "pages/expenses.html",
  "plan": 1500, "plan_by_month": {"2026-08": 2000}, "income": null, "savings_goal": null,
  "small_share": 0.03, "opaque": ["other"],
  "category_names": {"food": "Food"}, "months": [], "labels": {},
  "notes": {"spent": "", "income": "", "left": ""},
  "monthly_file": null, "columns": {"month": "month", "category": "category", "amount": "amount"}
}
```

`notes` are the owner's own sentences under the three cards. `monthly_file` and `columns` let an ICM
that already keeps a monthly aggregate under other names use it as it is.

When `language` in `_config/setup.json` is not English, fill `labels` (keys in `LABELS` of
`scripts/build-expenses-page.py`), `months` and `category_names` in that language now; a page half in
English reads as broken. Ask whether a refund should lower the category it came from: the page shows
**gross** money out, and a refund is simply not an expense.

`_config/expenses/categories.csv` with the header `pattern,category` and no rows: rows are earned by real statements.

Also: create the money area if there is none (`CONTEXT.md` and `output/expenses-state.md`: which
statements are in, how many rows, the last date), add its routing row and a procedures row for
`core/workflows/expenses/` to the instruction file, and list the owner's parser in `skills/CONTEXT.md`.
The built page holds aggregates only, so it may be committed; publishing it is the adapter's "publish a page".

## First run and proof

1. Build the parser together, from `recipes/statement-parser.md`, on one statement.
2. `categorize.py`, `aggregate.py`, `build-expenses-page.py`.
3. Proof: `aggregate.py` reconciled every statement, and the month total on the page equals what the
   owner reads off the statement for money out.
