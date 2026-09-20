#!/usr/bin/env python3
"""Fill the category column of transactions.csv from the owner's rules. Usage: categorize.py [--check]

Rules live in _config/expenses/categories.csv: pattern (a regular expression, matched case
insensitively against the description), category. First match wins.

invariant: a pattern is added only once it has really appeared in a statement, and whatever matches
nothing stays `other`. Admitting that a category is unknown beats guessing; the share of `other`
printed at the end is the number to watch, not something to hide.
A row that already has a category is left alone: a category set by the owner outranks a rule.
Money in is not an expense: rows with an amount of zero or more are left without a category and
are not counted in the share of `other`.
"""
import csv
import os
import re
import sys

from common import ROOT, data


def load_rules(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return [(re.compile(r["pattern"], re.I), r["category"]) for r in csv.DictReader(l for l in f if not l.startswith("#"))]


def categorize(description, rules):
    for rx, cat in rules:
        if rx.search(description or ""):
            return cat
    return "other"


def _check():
    rules = [(re.compile(r"grocer|market", re.I), "food"), (re.compile(r"\brail\b", re.I), "transport")]
    assert categorize("CITY MARKET 12", rules) == "food"
    assert categorize("National Rail ticket", rules) == "transport"
    assert categorize("trailer hire", rules) == "other"          # \b keeps "rail" out of "trailer"
    assert categorize("", rules) == "other" and categorize(None, rules) == "other"
    print("ok")


def main():
    src = data("transactions.csv")
    if not os.path.exists(src):
        print("0 transactions: %s does not exist yet" % os.path.relpath(src, ROOT)); return 1
    rules = load_rules(os.path.join(ROOT, "_config/expenses/categories.csv"))
    with open(src, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f); fields = reader.fieldnames; rows = list(reader)
    changed = 0
    out = [r for r in rows if float(r["amount"]) < 0]
    for r in out:
        if not (r.get("category") or "").strip():
            r["category"] = categorize(r.get("description"), rules); changed += 1
    with open(src, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    other = sum(1 for r in out if r["category"] == "other")
    print("%d rows, %d of them money out, %d newly categorized, %d rules, other: %d (%d%% of money out)" % (
        len(rows), len(out), changed, len(rules), other, round(100 * other / len(out)) if out else 0))
    return 0


if __name__ == "__main__":
    # invariant: an unknown flag stops the run. This script writes files, and a flag that is silently
    # ignored (`--help` did this) writes them for someone who only asked a question.
    unknown = [a for a in sys.argv[1:] if a.startswith("-") and a != "--check"]
    if unknown:
        print(__doc__ if unknown == ["--help"] else "unknown flag: %s; known: --check" % " ".join(unknown))
        sys.exit(0 if unknown == ["--help"] else 2)
    sys.exit(_check() or 0) if "--check" in sys.argv else sys.exit(main())
