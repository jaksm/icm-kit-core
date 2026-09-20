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
  "small_share": 0.03, "opaque": ["other", "cash"],
  "category_names": {"food": "Food"}, "months": [], "labels": {},
  "notes": {"spent": "", "income": "", "left": ""},
  "monthly_file": null, "columns": {"month": "month", "category": "category", "amount": "amount"}
}
```

`notes` are the owner's own sentences under the three cards. `monthly_file` and `columns` let an ICM
that already keeps a monthly aggregate under other names use it as it is.

`_config/expenses/categories.csv` with the header `pattern,category` and no rows: rows are earned by real statements.

## First run and proof

1. Build the parser together, from `recipes/statement-parser.md`, on one statement.
2. `categorize.py`, `aggregate.py`, `build-expenses-page.py`.
3. Proof: `aggregate.py` reconciled every statement, and the month total on the page equals what the
   owner reads off the statement for money out.
