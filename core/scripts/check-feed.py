#!/usr/bin/env python3
"""Judge a feed by its body, not by its HTTP code. Usage: check-feed.py <url> [<url> ...]

invariant: 200 is not a verdict. The common fake feed is a 200 with an HTML page; a repo without
releases serves valid Atom with zero entries; a hijacked domain serves spam through an old feed URL.
So the verdict comes from parsing the body and looking at what is in it.

Output is one line per feed, tab separated: verdict, items, newest, title, url. Verdicts:
  ok          a feed with at least one item
  empty       a valid feed with 0 items (say so; do not treat it as broken)
  not-a-feed  the body is HTML or something else
  stale       newest item older than --stale-days (default 365)
  unreachable network error or HTTP error, with the reason
Exit code: 0 if every feed is ok, 1 otherwise, 2 on bad usage.
"""
import datetime
import email.utils
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (compatible; icm-kit check-feed)"}


def when(text):
    text = (text or "").strip()
    if not text:
        return None
    try:
        return email.utils.parsedate_to_datetime(text).replace(tzinfo=None)
    except (TypeError, ValueError, IndexError):
        pass
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)
    return datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def judge(url, stale_days):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            body = r.read(3_000_000)
    except Exception as e:  # any network or HTTP failure is one verdict, with its reason
        return "unreachable", 0, "", str(e)[:80]
    head = body[:600].lstrip().lower()
    if head.startswith(b"<!doctype html") or head.startswith(b"<html"):
        return "not-a-feed", 0, "", "the body is an HTML page"
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        return "not-a-feed", 0, "", "not XML: %s" % str(e)[:60]
    tag = root.tag.split("}")[-1].lower()
    if tag not in ("rss", "feed", "rdf"):
        return "not-a-feed", 0, "", "root element is <%s>" % tag
    local = lambda e: e.tag.split("}")[-1].lower()
    items = [e for e in root.iter() if local(e) in ("item", "entry")]
    title = next((e.text or "" for e in root.iter() if local(e) == "title"), "").strip()[:60]
    dates = [d for d in (when(c.text) for it in items for c in it if local(c) in ("pubdate", "published", "updated", "date")) if d]
    newest = max(dates) if dates else None
    if not items:
        return "empty", 0, "", title
    if newest and (datetime.datetime.now() - newest).days > stale_days:
        return "stale", len(items), newest.date().isoformat(), title
    return "ok", len(items), newest.date().isoformat() if newest else "", title


def main(argv):
    stale = 365
    if "--stale-days" in argv:
        i = argv.index("--stale-days"); stale = int(argv[i + 1]); del argv[i:i + 2]
    urls = [a for a in argv if not a.startswith("-")]
    unknown = [a for a in argv if a.startswith("-")]
    if unknown or not urls:
        print(__doc__ if unknown in ([], ["--help"]) else "unknown flag: %s" % " ".join(unknown))
        return 0 if unknown == ["--help"] else 2
    bad = 0
    for u in urls:
        verdict, n, newest, note = judge(u, stale)
        bad += verdict != "ok"
        print("\t".join([verdict, "%d items" % n, newest or "-", note or "-", u]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
