"""Shared by the expenses scripts: where the ICM root, the config and the data folder are."""
import json
import os

# invariant: installed at <icm>/core/workflows/expenses/scripts/, so the ICM root is five folders up
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
DEFAULTS = {
    "data": "domains/money/data", "currency": "EUR", "out": "pages/expenses.html",
    "plan": None, "plan_by_month": {}, "income": None, "savings_goal": None,
    "small_share": 0.03, "opaque": ["other"], "category_names": {}, "months": [],
    "notes": {"spent": "", "income": "", "left": ""}, "labels": {},
    "monthly_file": None, "columns": {},
}


def config():
    c = dict(DEFAULTS)
    p = os.path.join(ROOT, "_config/expenses.json")
    if os.path.exists(p):
        c.update(json.load(open(p, encoding="utf-8")))
    return c


def data(name):
    return os.path.join(ROOT, config()["data"], name)
