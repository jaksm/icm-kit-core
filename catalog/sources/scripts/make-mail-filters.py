#!/usr/bin/env python3
"""Build a Gmail filter file from _config/sources/senders.csv. Usage: make-mail-filters.py [--check]

invariant: the CSV is the canonical source, the XML is a build output. A filter made by hand in the
mail settings and not written back to the CSV will be missing the next time this file is imported
into a new account, and nobody will know why mail stopped being sorted.

CSV columns: sender (an address, a domain, or several joined with OR), label, keep_in_inbox (yes/no),
why (free text, not exported). Lines starting with # are skipped.
Writes _config/sources/mail-filters.xml. Import it in the mail settings; importing beats clicking.
"""
import csv
import os
import sys
from xml.sax.saxutils import quoteattr

# invariant: installed at <icm>/core/workflows/sources/scripts/, so the ICM root is five folders up
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
SRC = os.path.join(ROOT, "_config/sources/senders.csv")
OUT = os.path.join(ROOT, "_config/sources/mail-filters.xml")


def build(rows):
    out = ["<?xml version='1.0' encoding='UTF-8'?>",
           "<feed xmlns='http://www.w3.org/2005/Atom' xmlns:apps='http://schemas.google.com/apps/2006'>",
           "  <title>Mail Filters</title>"]
    for r in rows:
        out += ["  <entry>", "    <category term='filter'/>",
                "    <apps:property name='from' value=%s/>" % quoteattr(r["sender"]),
                "    <apps:property name='label' value=%s/>" % quoteattr(r["label"])]
        if r["keep_in_inbox"].strip().lower() not in ("yes", "y", "true", "1"):
            out.append("    <apps:property name='shouldArchive' value='true'/>")
        out.append("  </entry>")
    return "\n".join(out + ["</feed>", ""])


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(l for l in f if not l.lstrip().startswith("#"))]
    for i, r in enumerate(rows, 2):
        for k in ("sender", "label", "keep_in_inbox"):
            assert (r.get(k) or "").strip(), "senders.csv line %d: %s is empty" % (i, k)
    return rows


def _check():
    rows = [{"sender": "news@example.com", "label": "Newsletters/Tech", "keep_in_inbox": "no"},
            {"sender": "tax.example.org OR \"O'Brien\" <a&b@example.org>", "label": "State", "keep_in_inbox": "yes"}]
    x = build(rows)
    import xml.etree.ElementTree as ET
    root = ET.fromstring(x)   # quotes, ampersands and apostrophes in a sender must not break the file
    ns = {"a": "http://www.w3.org/2005/Atom", "apps": "http://schemas.google.com/apps/2006"}
    entries = root.findall("a:entry", ns)
    assert len(entries) == 2
    props = [{p.get("name"): p.get("value") for p in e.findall("apps:property", ns)} for e in entries]
    assert props[0].get("shouldArchive") == "true" and "shouldArchive" not in props[1]
    assert props[1]["from"] == rows[1]["sender"]
    print("ok")


if __name__ == "__main__":
    if "--check" in sys.argv:
        _check(); sys.exit(0)
    if not os.path.exists(SRC):
        print("0 senders: %s does not exist yet" % os.path.relpath(SRC, ROOT)); sys.exit(1)
    rows = read(SRC)
    open(OUT, "w", encoding="utf-8").write(build(rows))
    print("%d filters written to %s" % (len(rows), os.path.relpath(OUT, ROOT)))
