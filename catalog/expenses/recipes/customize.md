---
trust_tier: unverified
---

# Fitting the page

Configuration first: names, plan, notes, labels are all in `_config/expenses.json`. For a different
layout, copy `template/expenses-template.html` to
`_config/overrides/core/workflows/expenses/template/` and change the copy; the builder looks there
first. Keep the rule that no script draws the numbers: state in CSS, bars as elements.

A second view (a year, a comparison of two people who share costs) is a new builder in the owner's
`skills/`, reading the same `monthly.csv`. Shared costs between people are a different workflow: who
paid and who owes is exactly what this one refuses to hold.

The template is one self-contained page: its colors are tokens on `:root` with a dark set under `prefers-color-scheme`, no library. `--demo` builds the page from mock data into `<tmp>/icm-kit-demo/expenses.html`, which is the quickest way to see a change without your base.
