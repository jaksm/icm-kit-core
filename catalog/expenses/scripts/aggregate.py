#!/usr/bin/env python3
"""transactions.csv into monthly.csv: spending per month and category. Usage: aggregate.py [--check]

transactions.csv columns: date (YYYY-MM-DD), description, amount (negative is money out), currency,
category, statement. Optional: balance (running balance after the row).

invariant: monthly.csv is the only file answers and pages are built from. It holds no description,
no counterparty and no single transaction, so what reaches a conversation is an aggregate by construction.
invariant: when rows carry a balance, each statement must reconcile: the sum of its amounts equals its
last balance minus the balance before its first row. A statement that does not reconcile stops the run,
because a parser that drops or doubles a row produces totals that look entirely plausible.
"""
import collections
import csv
import os
import sys

from common import ROOT, data


def reconcile(rows):
    """Return a list of (statement, difference) for statements whose amounts do not add up to their balances."""
    by = collections.defaultdict(list)
    for r in rows:
        if (r.get("balance") or "").strip():
            by[r["statement"]].append(r)
    bad = []
    for st, rs in by.items():
        # invariant: a stable sort by date keeps the statement's own order within a day, which the
        # parser's contract guarantees; the opening balance is derived from the first row
        rs.sort(key=lambda r: r["date"])
        opening = float(rs[0]["balance"]) - float(rs[0]["amount"])
        diff = round(sum(float(r["amount"]) for r in rs) - (float(rs[-1]["balance"]) - opening), 2)
        if diff:
            bad.append((st, diff))
    return bad


def monthly(rows):
    out = collections.defaultdict(lambda: [0.0, 0])
    for r in rows:
        a = float(r["amount"])
        if a < 0:                                   # spending only; money in is not an expense
            k = (r["date"][:7], (r.get("category") or "other").strip() or "other")
            out[k][0] += -a; out[k][1] += 1
    return [{"month": m, "category": c, "amount": "%.2f" % v[0], "count": v[1]} for (m, c), v in sorted(out.items())]


def _check():
    rows = [{"date": "2026-01-03", "amount": "-10.00", "category": "food", "statement": "s1", "balance": "90.00"},
            {"date": "2026-01-09", "amount": "-5.50", "category": "", "statement": "s1", "balance": "84.50"},
            {"date": "2026-01-20", "amount": "100.00", "category": "income", "statement": "s1", "balance": "184.50"}]
    assert reconcile(rows) == []
    m = monthly(rows)
    assert m == [{"month": "2026-01", "category": "food", "amount": "10.00", "count": 1},
                 {"month": "2026-01", "category": "other", "amount": "5.50", "count": 1}], m
    rows[1]["amount"] = "-6.50"                      # a misread amount must be caught
    assert reconcile(rows) == [("s1", -1.0)], reconcile(rows)
    print("ok")


def main():
    src = data("transactions.csv")
    if not os.path.exists(src):
        print("0 transactions: %s does not exist yet" % os.path.relpath(src, ROOT)); return 1
    rows = list(csv.DictReader(open(src, encoding="utf-8", newline="")))
    bad = reconcile(rows)
    if bad:
        for st, d in bad:
            print("does not reconcile: statement %s is off by %.2f" % (st, d))
        return 1
    out = monthly(rows)
    with open(data("monthly.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["month", "category", "amount", "count"]); w.writeheader(); w.writerows(out)
    print("%d rows in, %d month and category rows out, %d months" % (len(rows), len(out), len({r["month"] for r in out})))
    return 0


if __name__ == "__main__":
    sys.exit(_check() or 0) if "--check" in sys.argv else sys.exit(main())
