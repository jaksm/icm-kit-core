---
trust_tier: unverified
---

# A parser for the owner's bank statements

Read `core/RECIPES.md` first. As a whole this has not been run. The points marked **(from use)** come
from a parser built this way for one bank's PDF statements and used on two years of them.

There is no ready parser, on purpose: every bank's format is its own, and it changes. You build one
for this owner, in `skills/<name>/scripts/` of **their** ICM, never in `core/`.

## Before writing code

1. Ask for the export the bank offers. **CSV or a spreadsheet beats PDF every time**; many banks
   have it one menu away from the PDF. Statements are saved **outside** the ICM: the ICM gets the rows, not the documents.
2. Look at one statement with the owner. Find: the date column, the description, money out and in
   (one signed column or two), the running balance, the currency, and where a foreign amount appears.
3. Never print a statement whole into the conversation. Quote a few lines with the digits of
   account numbers replaced, to agree on the columns.

## The contract

Write `<data>/transactions.csv` with the header
`date,description,amount,currency,category,statement,balance`: ISO date; `amount` negative for money
out; `category` left empty; `statement` an id for the document (its period); `balance` the running
balance after the row, when the statement has one. **Rows are written in the order of the
statement**: two rows of one day must keep their order, or the balances stop adding up. Importing a
statement id that is already in **skips** it and says so: replacing would wipe categories the owner
fixed by hand. A corrected statement is imported after its old rows were deleted on the owner's word.

The parser finds the data folder by reading the `data` key of `_config/expenses.json` (default
`domains/money/data`), not by importing anything from `core/`.

## Hard points

- In a CSV or text export, read the amount column, and **stop the import if an amount differs from
  the change between two consecutive balances**. Lines above the header often carry the account
  number and the owner's full name: useful for the statement id and as names to strip, never to be copied.
- **(from use)** In a PDF, do not read amounts from their columns. Text extraction glues columns
  together without spaces and in an unreliable order; a first attempt that way produced hundreds of
  rows of which none passed a check. Read the **running balance** only, and derive each amount as
  the difference between two consecutive balances. Then every row checks itself, and the sum of all
  changes must equal the last balance minus the first.
- **(from use)** **Privacy is in the code, not in discipline.** Strip account numbers, card numbers
  and the names of people from the description before the row is written. What never reaches the
  CSV cannot leak from it. Numbers are easy; names have no general solution. Strip the owner's own
  name (from the statement), the words after the bank's phrases for "transfer to" and "from", and
  the first names listed in `who-am-i.md`; say in a comment in the parser that this is the ceiling.
  Short numbers such as a shop's branch number may stay.
- Decimal and thousands separators differ by country; detect them from the balance column, do not assume.
- A refund is money in with a merchant's description; it stays a positive amount and is not an expense.
- Transfers between the owner's own accounts are not spending. Ask how they want them marked.

## Proof

`core/workflows/expenses/scripts/aggregate.py` reconciles every statement to zero. The parser has
its own `--check` on **synthetic** rows written for the test, never on the owner's real ones. The
description column holds no account number, `grep -E '[0-9]{8,}' transactions.csv` prints nothing,
and no name: grep for the owner's name and for every first name in `who-am-i.md` prints nothing.

## When to say no

A bank that offers only a scanned image. Then the owner types the month's total per category, and
`monthly.csv` is written by hand; the page works the same.
