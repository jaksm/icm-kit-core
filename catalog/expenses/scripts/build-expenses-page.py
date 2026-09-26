#!/usr/bin/env python3
"""Build the expenses page from monthly.csv. Usage: build-expenses-page.py [--check | --demo]

--demo builds the page from the mock months in template/demo/ (no _config, no base) into <tmp>/icm-kit-demo/expenses.html,
so the look can be judged and refined without anyone's real numbers.

invariant: the page is built from the monthly aggregate only. It cannot show a transaction, because
it never reads one.
invariant: nothing about the owner is in this file. Plan, income, goal, names of categories and
months, the notes under the cards and every label come from _config/expenses.json; without them the
page shows spending alone, in English.
The template is one self-contained page (tokens on :root, both themes); this file only fills it. State is CSS
(one radio input per month), bars are plain elements and the trend is inline SVG, so the numbers are there even
where scripts do not run.
"""
import collections
import csv
import json
import html
import os
import re
import sys

from common import ROOT, config, data

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# invariant: a category's color is a token of the template, by rank: --cat-1..8 for the largest eight, the grey tail
# --cat-9..12 after that and for the folded "small items" line. No color is written in this file.
CATS, TAIL_FROM, SMALL = 8, 9, "var(--cat-10)"
LABELS = {
    "title": "Expenses by month", "months": "Months", "spent": "Spent", "income": "Income", "left": "Left over",
    "above": "above", "below": "below", "planOf": "the plan of", "goal": "goal", "total": "total",
    "smallItems": "small items", "inSmall": "In small items:", "largest": "Largest item",
    "topThree": "The top three carry", "ofMonth": "of the month", "opaque": "Without a real category",
    "vsPrev": "Against the month before", "more": "more than", "less": "less than", "caption": "Spending by category,",
    "trend": "spent, the months up to this one",
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
    color = {k: "var(--cat-%d)" % (i + 1 if i < CATS else TAIL_FROM + (i - CATS) % 4) for i, (k, _) in enumerate(total.most_common())}
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
    return ('<div class="card"><p class="caption">%s</p><span class="num%s">%s<small>%s</small></span>%s%s</div>'
            % (E(title), cls, money(value), E(cur), '<p class="text is-small">%s</p>' % sub if sub else "",
               '<p class="caption">%s</p>' % E(note) if note else ""))


def panel(i, m, row, color, prev, cfg, L, name, month_name, trend=""):
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
        state = "" if goal is None else (" is-good" if left >= goal else " is-warn" if left >= goal * 0.75 else " is-bad")
        cards += card(L["income"], cfg["income"], "", cfg["notes"].get("income"), cur)
        cards += card(L["left"], left, "%s %s %s" % (L["goal"], money(goal), E(cur)) if goal is not None else "", cfg["notes"].get("left"), cur, state)
    rows = "".join(
        '<tr%s><th scope="row"><span class="dot" style="--dot:%s"></span> %s</th>'
        '<td class="bar"><div style="--v:%.1f%%;--bar:%s"><i></i></div></td><td class="is-num">%s&nbsp;%s</td><td class="is-num">%d%%</td></tr>'
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
    foot = '<p class="caption">%s %s.</p>' % (L["inSmall"], E(", ".join(name(k) for k in folded))) if folded else ""
    return ('<section class="panel p%d" aria-label="%s"><div><div class="grid">%s</div>'
            '<div class="block"><table><caption class="sr">%s %s</caption>'
            '<tbody>%s</tbody><tfoot><tr><th scope="row">%s</th><td class="bar"></td><td class="is-num">%s&nbsp;%s</td><td class="is-num">100%%</td></tr></tfoot></table>%s</div>'
            '%s<dl class="facts">%s</dl></div></section>' % (i, E(month_name(m)), cards, L["caption"], E(month_name(m)), rows, L["total"], money(total), E(cur), foot,
                                       trend, "".join('<div><dt class="caption">%s</dt><dd class="text">%s</dd></div>' % (E(a), b) for a, b in facts)))


def page(by_month, color, cfg):
    L = {**LABELS, **cfg["labels"]}
    names = cfg["months"] if len(cfg["months"]) == 12 else MONTHS
    month_name = lambda m: "%s %s" % (names[int(m[5:7]) - 1], m[:4])
    name = lambda k: cfg["category_names"].get(k, k)
    ms = list(by_month)
    # one radio per month; :has() shows the month's panel, still with no script
    # newest first and short names: the strip scrolls sideways on a phone, and with no script the checked month must already be in view
    short = lambda m: "%s %s" % (names[int(m[5:7]) - 1][:3], m[:4])
    tabs = "".join('<label><input type="radio" name="m" id="m%d"%s aria-label="%s"><span>%s</span></label>'
                   % (i, " checked" if i == len(ms) - 1 else "", E(month_name(m)), E(short(m))) for i, m in reversed(list(enumerate(ms))))
    totals = [int(round(sum(by_month[m].values()))) for m in ms]

    def trend(i):   # the months up to this one as inline SVG bars on a zero baseline; a single month has no trend to show
        v = totals[max(0, i - 5):i + 1]
        if len(v) < 2:
            return ""
        W, H, pad, hi = 210, 34, 3, max(v + [1])
        slot = (W - 2 * pad) / len(v); w = slot * 0.62
        bars = "".join('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"%s/>'
                       % (pad + j * slot + (slot - w) / 2, H - pad - t * (H - 2 * pad) / hi, w, max(1, t * (H - 2 * pad) / hi),
                          ' class="is-last"' if j == len(v) - 1 else "") for j, t in enumerate(v))
        return '<div class="trend"><svg viewBox="0 0 %d %d" preserveAspectRatio="none" aria-hidden="true">%s</svg><p class="caption">%s</p></div>' % (W, H, bars, E(L["trend"]))
    panels = "".join(panel(i, m, by_month[m], color, (month_name(ms[i - 1]), sum(by_month[ms[i - 1]].values())) if i else None,
                           cfg, L, name, month_name, trend(i)) for i, m in enumerate(ms))
    rules = "\n".join(".page:has(#m%d:checked) .p%d{display:block}" % (i, i) for i in range(len(ms)))
    t = open(os.path.join(HERE, "template/expenses-template.html"), encoding="utf-8").read()
    own = os.path.join(ROOT, "_config/overrides/core/workflows/expenses/template/expenses-template.html")
    if os.path.exists(own):
        t = open(own, encoding="utf-8").read()
    for k, v in L.items():
        t = t.replace("{{%s}}" % k, E(v))
    left = re.findall(r"\{\{\w+\}\}", t)
    assert not left, "template tokens without a label: %s" % sorted(set(left))
    return t.replace("__RULES__", rules).replace("__TABS__", tabs).replace("__PANELS__", panels)


def _check():
    from common import DEFAULTS
    cfg = {**DEFAULTS, "plan": 1000, "income": 1500}
    by = {"2026-01": {"food": 400.0, "rent": 500.0, "other": 20.0, "gifts": 10.0}, "2026-02": {"food": 300.0, "rent": 500.0}}
    items, total = arrange(by["2026-01"], 0.03, LABELS)
    assert total == 930 and items[0][0] == "rent" and items[-1][2] == ["other", "gifts"], items
    color = {k: "var(--cat-%d)" % (i + 1) for i, k in enumerate(["rent", "food", "other", "gifts"])}
    out = page(by, color, cfg)
    assert out.count('class="panel p') == 2 and 'id="m1" checked' in out and "70 EUR below the plan of 1,000 EUR" in out, "plan line"
    assert "num is-good" in out                # 1500 - 930 = 570 against a goal of 500
    assert ".page:has(#m1:checked) .p1{display:block}" in out and '<div class="trend"><svg' in out
    assert not re.search(r"#[0-9a-fA-F]{6}\b", out.split("</style>")[1]), "a literal color outside the tokens"
    assert "{{" not in out and "__" not in out.split("</style>")[1][:50]
    cfg2 = {**DEFAULTS}                         # with no plan and no income the page is spending alone
    assert "Income" not in page(by, color, cfg2)
    demo(write=False)                          # the mock months must always build
    print("ok")


def demo(write=True):
    """The page from the mock months beside the template. Nothing of the owner's is read."""
    d = os.path.join(HERE, "template/demo")
    from common import DEFAULTS
    cfg = {**DEFAULTS, **json.load(open(os.path.join(d, "config.json"), encoding="utf-8")), "monthly_file": os.path.join(d, "monthly.csv")}
    by, color = load(cfg)
    html_ = page(by, color, cfg)
    if not write:
        return 0
    import tempfile
    out = os.path.join(tempfile.gettempdir(), "icm-kit-demo/expenses.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html_)
    print("wrote %s, %d months, %d categories" % (out, len(by), len(color)))
    return 0


def main():
    cfg = config()
    by, color = load(cfg)
    if not by:
        print("0 months: the monthly file is empty"); return 1
    out = os.path.join(ROOT, cfg["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page(by, color, cfg))
    print("wrote %s, %d B, %d months, %d categories" % (os.path.relpath(out, ROOT), os.path.getsize(out), len(by), len(color)))
    return 0


if __name__ == "__main__":
    # invariant: an unknown flag stops the run. This script writes files, and a flag that is silently
    # ignored (`--help` did this) writes them for someone who only asked a question.
    unknown = [a for a in sys.argv[1:] if a.startswith("-") and a not in ("--check", "--demo")]
    if unknown:
        print(__doc__ if unknown == ["--help"] else "unknown flag: %s; known: --check, --demo" % " ".join(unknown))
        sys.exit(0 if unknown == ["--help"] else 2)
    sys.exit((_check() or 0) if "--check" in sys.argv else demo() if "--demo" in sys.argv else main())
