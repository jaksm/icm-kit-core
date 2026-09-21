#!/usr/bin/env python3
"""Build every page of the kit from its mock data into previews/, plus an index. Usage: scripts/build-previews.py
For judging and refining the look without anyone's base: nothing of an owner's is read, previews/ is not committed.
Serve it:  python3 -m http.server 8914 --directory previews
A builder without --demo yet is listed as pending, not failed."""
import importlib.util
import os
import subprocess
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = [("expenses", "catalog/expenses/scripts/build-expenses-page.py", "A month of spending: tabs without script, stat cards, the category table, the trend."),
         ("graph", "core/workflows/graph/scripts/build-graph-page.py", "The base as a graph: search, the panel of a record, legend, settings."),
         ("feed", "catalog/feed/scripts/build-feed-page.py", "The daily feed: rows of cards over photos, details, actions, the comment sheet.")]

rows = []
for name, script, about in PAGES:
    src = open(os.path.join(KIT, script), encoding="utf-8").read()
    ok = '"--demo"' in src and subprocess.run([sys.executable, os.path.join(KIT, script), "--demo"], cwd=KIT).returncode == 0
    rows.append('<a class="icm-row" href="%s.html"%s><span><b>%s</b><br><span class="icm-caption">%s</span></span><span class="icm-badge %s">%s</span></a>'
                % (name, "" if ok else ' aria-disabled="true" tabindex="-1" style="pointer-events:none;opacity:.55"', name, about,
                   "is-good" if ok else "", "mock data" if ok else "not migrated yet"))
spec = importlib.util.spec_from_file_location("icmlib", os.path.join(KIT, "core/ui/build.py"))
lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)
page = """<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>icm-kit previews</title>
<!--ICM-FONTS--><style>/*ICM-CSS*/
body{margin:0;background:var(--paper)}</style><body class="on-paper"><main class="icm-page"><div class="icm-stack is-loose">
<div class="icm-stack is-tight"><h1 class="icm-title">Previews</h1><p class="icm-text is-2">Every page the kit builds, from mock data. Add <span class="icm-mono">?theme=dark</span> or <span class="icm-mono">?theme=light</span> to any of them.</p></div>
<div class="icm-card is-list">%s</div></div></main><script type="module">/*ICM-JS*/</script>""" % "".join(rows)
os.makedirs(os.path.join(KIT, "previews"), exist_ok=True)
open(os.path.join(KIT, "previews/index.html"), "w", encoding="utf-8").write(lib.inline(page))
print("wrote previews/index.html")
