#!/usr/bin/env python3
"""Build the expenses page from monthly.csv. Usage: build-expenses-page.py [--check]

invariant: the page is built from the monthly aggregate only. It cannot show a transaction, because
it never reads one.
invariant: nothing about the owner is in this file. Plan, income, goal, names of categories and
months, the notes under the cards and every label come from _config/expenses.json; without them the
page shows spending alone, in English.
State is CSS (one radio input per month) and bars are plain elements, so the numbers are there even
where scripts do not run.
"""
import collections
import csv
import html
import importlib.util
import os
import re
import sys

from common import ROOT, config, data

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = ["#b0643f", "#c9a052", "#7f8a4e", "#9c7a63", "#a3574f", "#8f8568", "#c48b6e", "#6f7a6a"]
TAIL = ["#9c9a92", "#b0aea5", "#87867f", "#c2c0b6"]
SMALL = "#a8a69e"
LABELS = {
    "title": "Expenses by month", "months": "Months", "spent": "Spent", "income": "Income", "left": "Left over",
    "above": "above", "below": "below", "planOf": "the plan of", "goal": "goal", "total": "total",
    "smallItems": "small items", "inSmall": "In small items:", "largest": "Largest item",
    "topThree": "The top three carry", "ofMonth": "of the month", "opaque": "Without a real category",
    "vsPrev": "Against the month before", "more": "more than", "less": "less than", "caption": "Spending by category,",
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
E = html.escape


def money(n):
    return format(int(round(n)), ",d")


def load(cfg):
    path = os.path.join(ROOT, cfg.get("monthly_file") or os.path.join(cfg["data"], "monthly.csv"))
    col = {"month": "month", "category": "category", "amount": "amount", **cfg.get("columns", {})}
    by, total = collections.defaultdict(dict), collections.Counter()
    for r in csv.DictReader(open(path, encoding="utf-8", newline="")):
        v = round(float(r[col["amount"]]), 2)
        by[r[col["month"]]][r[col["category"]]] = by[r[col["month"]]].get(r[col["category"]], 0) + v
        total[r[col["category"]]] += v
    color = {k: (INK[i] if i < len(INK) else TAIL[(i - len(INK)) % len(TAIL)]) for i, (k, _) in enumerate(total.most_common())}
    return dict(sorted(by.items())), color


def arrange(row, small_share, L):
    """Largest first; categories under the small share are folded into one line."""
    total = sum(row.values())
    big = sorted(((k, v) for k, v in row.items() if v / total >= small_share), key=lambda t: -t[1])
    small = sorted(((k, v) for k, v in row.items() if v / total < small_share), key=lambda t: -t[1])
    items = [(k, v, None) for k, v in big]
    if small:
        items.append((L["smallItems"], sum(v for _, v in small), [k for k, _ in small]))
    return items, total


def card(title, value, sub, note, cur, cls=""):
    return ('<div class="card"><p class="k">%s</p><p class="v%s">%s<span>%s</span></p><p class="s">%s</p>%s</div>'
            % (E(title), cls, money(value), E(cur), sub, '<p class="n">%s</p>' % E(note) if note else ""))


def panel(i, m, row, color, prev, cfg, L, name, month_name):
    items, total = arrange(row, cfg["small_share"], L)
    cur, plan = cfg["currency"], cfg["plan_by_month"].get(m, cfg["plan"])
    sub = ""
    if plan is not None:
        d = total - plan
        sub = "%s %s %s %s %s %s" % (money(abs(d)), E(cur), L["above"] if d > 0 else L["below"], L["planOf"], money(plan), E(cur))
    cards = card(L["spent"], total, sub, cfg["notes"].get("spent"), cur)
    if cfg["income"] is not None:
        left = cfg["income"] - total
        goal = cfg["savings_goal"] if cfg["savings_goal"] is not None else (cfg["income"] - plan if plan is not None else None)
        state = "" if goal is None else (" good" if left >= goal else " near" if left >= goal * 0.75 else " bad")
        cards += card(L["income"], cfg["income"], "", cfg["notes"].get("income"), cur)
        cards += card(L["left"], left, "%s %s %s" % (L["goal"], money(goal), E(cur)) if goal is not None else "", cfg["notes"].get("left"), cur, state)
    rows = "".join(
        '<tr%s><th scope="row"><span class="dot" style="background:%s"></span>%s</th>'
        '<td class="bar"><span style="width:%.1f%%;background:%s"></span></td><td class="num">%s&nbsp;%s</td><td class="pct">%d%%</td></tr>'
        % (' class="small"' if folded else "", SMALL if folded else color[k], E(k if folded else name(k)),
           v / items[0][1] * 100, SMALL if folded else color[k], money(v), E(cur), round(v / total * 100))
        for k, v, folded in items)
    top = items[0]
    facts = [(L["largest"], "%s, %s %s" % (E(top[0] if top[2] else name(top[0])), money(top[1]), E(cur))),
             (L["topThree"], "%d%% %s" % (round(sum(v for _, v, _ in items[:3]) / total * 100), L["ofMonth"])),
             (L["opaque"], "%d%% %s" % (round(sum(v for k, v in row.items() if k in cfg["opaque"]) / total * 100), L["ofMonth"]))]
    if prev:
        d = total - prev[1]
        facts.append((L["vsPrev"], "%s %s %s %s" % (money(abs(d)), E(cur), L["more"] if d > 0 else L["less"], E(prev[0]))))
    folded = next((f for _, _, f in items if f), None)
    foot = '<p class="foot">%s %s.</p>' % (L["inSmall"], E(", ".join(name(k) for k in folded))) if folded else ""
    return ('<section class="panel p%d" aria-label="%s"><div class="cards">%s</div><table><caption class="sr">%s %s</caption>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">%s</th><td class="bar"></td><td class="num">%s&nbsp;%s</td><td class="pct">100%%</td></tr></tfoot></table>%s'
            '<dl>%s</dl></section>' % (i, E(month_name(m)), cards, L["caption"], E(month_name(m)), rows, L["total"], money(total), E(cur), foot,
                                       "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (E(a), b) for a, b in facts)))


def page(by_month, color, cfg):
    L = {**LABELS, **cfg["labels"]}
    names = cfg["months"] if len(cfg["months"]) == 12 else MONTHS
    month_name = lambda m: "%s %s" % (names[int(m[5:7]) - 1], m[:4])
    name = lambda k: cfg["category_names"].get(k, k)
    ms = list(by_month)
    radios = "".join('<input type="radio" name="m" id="m%d"%s>' % (i, " checked" if i == len(ms) - 1 else "") for i in range(len(ms)))
    tabs = "".join('<label for="m%d" class="t%d">%s</label>' % (i, i, E(month_name(m))) for i, m in enumerate(ms))
    panels = "".join(panel(i, m, by_month[m], color, (month_name(ms[i - 1]), sum(by_month[ms[i - 1]].values())) if i else None,
                           cfg, L, name, month_name) for i, m in enumerate(ms))
    rules = "\n".join("#m%d:checked ~ .panels .p%d{display:block}\n#m%d:checked ~ .tabs .t%d{color:var(--ink);border-color:var(--ink)}" % (i, i, i, i)
                      for i in range(len(ms)))
    t = open(os.path.join(HERE, "template/expenses-template.html"), encoding="utf-8").read()
    own = os.path.join(ROOT, "_config/overrides/core/workflows/expenses/template/expenses-template.html")
    if os.path.exists(own):
        t = open(own, encoding="utf-8").read()
    for k, v in L.items():
        t = t.replace("{{%s}}" % k, E(v))
    left = re.findall(r"\{\{\w+\}\}", t)
    assert not left, "template tokens without a label: %s" % sorted(set(left))
    return t.replace("__RULES__", rules).replace("__RADIOS__", radios).replace("__TABS__", tabs).replace("__PANELS__", panels)


def _lib():
    lib = os.environ.get("ICM_LIB") or os.path.join(ROOT, "core/ui")
    spec = importlib.util.spec_from_file_location("icmlib", os.path.join(lib, "build.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _check():
    from common import DEFAULTS
    cfg = {**DEFAULTS, "plan": 1000, "income": 1500}
    by = {"2026-01": {"food": 400.0, "rent": 500.0, "other": 20.0, "gifts": 10.0}, "2026-02": {"food": 300.0, "rent": 500.0}}
    items, total = arrange(by["2026-01"], 0.03, LABELS)
    assert total == 930 and items[0][0] == "rent" and items[-1][2] == ["other", "gifts"], items
    color = {"rent": INK[0], "food": INK[1], "other": INK[2], "gifts": INK[3]}
    out = page(by, color, cfg)
    assert out.count('class="panel p') == 2 and 'id="m1" checked' in out and "70 EUR below the plan of 1,000 EUR" in out, "plan line"
    assert "v good" in out                     # 1500 - 930 = 570 against a goal of 500
    assert "{{" not in out and "__" not in out.split("</style>")[1][:50]
    cfg2 = {**DEFAULTS}                         # with no plan and no income the page is spending alone
    assert "Income" not in page(by, color, cfg2)
    print("ok")


def main():
    cfg = config()
    by, color = load(cfg)
    if not by:
        print("0 months: the monthly file is empty"); return 1
    out = os.path.join(ROOT, cfg["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(_lib().inline(page(by, color, cfg)))
    print("wrote %s, %d B, %d months, %d categories" % (os.path.relpath(out, ROOT), os.path.getsize(out), len(by), len(color)))
    return 0


if __name__ == "__main__":
    sys.exit(_check() or 0) if "--check" in sys.argv else sys.exit(main())
