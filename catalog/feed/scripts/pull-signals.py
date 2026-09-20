#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["feedparser>=6.0.11"]
# ///
"""Steps 0 to 2 of the signal funnel: fetch every feed, dedupe, apply hard filters.

Writes one file per step into <data>/signals/<date>/ so the work can be checked afterwards.
Nothing here judges relevance; that is step 3 and it needs a model. Dropped rows always carry a
reason, because 02-dropped.csv is where a bad filter rule becomes visible.

    uv run pull-signals.py                  # today, every group
    uv run pull-signals.py --group a,b      # some groups, in one pass
    uv run pull-signals.py --check          # self-check, no network, writes nothing

Sources: _config/feed/feeds.csv (group,name,url) and, optional, _config/feed/channels.csv
(group,channel,channel_id). A row whose `status` column says `off` is skipped.
"""
import argparse, collections, csv, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, config, data

CFG = config()
FEEDS = Path(ROOT) / "_config/feed/feeds.csv"
CHANNELS = Path(ROOT) / "_config/feed/channels.csv"
OUT_BASE = Path(data("signals"))
SEEN = OUT_BASE / "seen.csv"
MAX_AGE_HOURS = CFG["max_age_hours"]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# invariant: reddit answers 429 when feeds are pulled back to back, and it is easy to conclude
# from that that reddit feeds are dead. They go through a serial lane with a gap between them;
# everything else runs concurrently.
REDDIT_GAP = CFG["reddit_gap"]


def is_reddit(url: str) -> bool:
    return "reddit.com" in url


def read_sources(groups, feeds=None, channels=None) -> list[dict]:
    rows = []
    feeds, channels = feeds or FEEDS, channels or CHANNELS
    with open(feeds, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            # a url with <placeholder> in it is a template for a query feed, not a feed
            if r["url"].startswith("http") and "<" not in r["url"] and r.get("status") != "off":
                rows.append({"group": r["group"], "name": r["name"], "url": r["url"]})
    if os.path.exists(channels):
        with open(channels, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("status") != "off":
                    rows.append({"group": "youtube-" + r["group"], "name": r["channel"],
                                 "url": "https://www.youtube.com/feeds/videos.xml?channel_id=" + r["channel_id"]})
    return [r for r in rows if groups is None or r["group"] in groups]


def entry_time(e):
    for key in ("published_parsed", "updated_parsed"):
        t = getattr(e, key, None)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def fetch(src: dict, retries: int = 1):
    """Return (items, error). feedparser never raises, so failure is read off the result."""
    import feedparser
    try:
        d = feedparser.parse(src["url"], agent=UA)
    except Exception as exc:  # a malformed feed must not kill the run
        return [], {**src, "error": type(exc).__name__, "detail": str(exc)[:200]}

    status = getattr(d, "status", 0)
    # invariant: the gap is a floor, not a guarantee, so 429 gets one slow retry.
    if status == 429 and retries > 0:
        time.sleep(REDDIT_GAP * 2)
        return fetch(src, retries - 1)
    if status >= 400:
        return [], {**src, "error": f"http-{status}", "detail": ""}
    if not d.entries:
        # a feed that parses but holds nothing: a dead channel, a blog that stopped. Not an
        # error, but it must be visible.
        # No status at all means the request never got an answer, which is a different repair.
        return [], {**src, "error": "empty" if status else "unreachable",
                    "detail": str(getattr(d, "bozo_exception", ""))[:200]}

    items = []
    for e in d.entries:
        ts = entry_time(e)
        # invariant: the cheapest honest image is the one the feed already hands over. Anything
        # not found here has to be fetched from the page later, one request per card.
        image = ""
        for t in getattr(e, "media_thumbnail", None) or []:
            if t.get("url"):
                image = t["url"]
                break
        if not image:
            for m in getattr(e, "media_content", None) or []:
                if m.get("url") and str(m.get("medium", "image")) == "image":
                    image = m["url"]
                    break
        if not image:
            for enc in getattr(e, "enclosures", None) or []:
                if str(enc.get("type", "")).startswith("image/"):
                    image = enc.get("href", "")
                    break
        items.append({
            "image": image, "group": src["group"], "source": src["name"], "feed_url": src["url"],
            "guid": getattr(e, "id", "") or getattr(e, "link", ""),
            "url": getattr(e, "link", ""),
            "title": re.sub(r"\s+", " ", getattr(e, "title", "")).strip(),
            # invariant: a video description can run past 2000 characters and is the only full
            # text there is when the transcript fails, so the cut is generous.
            "summary": re.sub(r"<[^>]+>", " ", getattr(e, "summary", ""))[:2500].strip(),
            "author": getattr(e, "author", ""),
            "published": ts.isoformat() if ts else "",
        })
    return items, None


def fetch_all(sources):
    reddit = [s for s in sources if is_reddit(s["url"])]
    other = [s for s in sources if not is_reddit(s["url"])]
    items, errors = [], []
    with ThreadPoolExecutor(max_workers=12) as pool:
        for got, err in pool.map(fetch, other):
            items += got
            if err:
                errors.append(err)
    for i, src in enumerate(reddit):
        if i:
            time.sleep(REDDIT_GAP)
        got, err = fetch(src)
        items += got
        if err:
            errors.append(err)
    return items, errors


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def dedupe(items):
    """Same story from three feeds is one item with three confirmations, not three cards."""
    keep, dupes = {}, []
    for it in items:
        for key in (it["guid"], it["url"], norm_title(it["title"])):
            if key and key in keep:
                keep[key]["confirmations"].append(it["source"])
                dupes.append({"title": it["title"], "source": it["source"],
                              "merged_into": keep[key]["source"], "key": key[:120]})
                break
        else:
            it = {**it, "confirmations": [it["source"]]}
            for key in (it["guid"], it["url"], norm_title(it["title"])):
                if key:
                    keep[key] = it
    # one dict is stored under several keys; id() collapses them back to unique objects
    return list({id(v): v for v in keep.values()}.values()), dupes


def load_seen(date: str, path=None) -> set:
    """Keys served on an EARLIER day.

    invariant: rows written on `date` itself are ignored, so running a day again is idempotent
    instead of destructive. Without this the second run of a day drops nearly everything as
    already seen.
    """
    path = path or SEEN
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8", newline="") as f:
        return {r["key"] for r in csv.DictReader(f) if r.get("date") != date}


def hard_filters(items, seen):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    passed, dropped = [], []
    for it in items:
        key = it["guid"] or it["url"]
        if key in seen:
            dropped.append({**it, "reason": "already-seen"})
        elif not it["url"]:
            dropped.append({**it, "reason": "no-url"})
        elif it["published"] and datetime.fromisoformat(it["published"]) < cutoff:
            dropped.append({**it, "reason": "too-old"})
        else:
            passed.append(it)
    return passed, dropped


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def write_csv(path, rows, fields):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def run(group, date: str) -> dict:
    # invariant: one run writes one set of files, so a run for one group must not clobber the
    # previous group's. --group takes a comma separated list and all of it lands in one pass.
    groups = {g.strip() for g in group.split(",")} if group else None
    out = OUT_BASE / date
    out.mkdir(parents=True, exist_ok=True)

    sources = read_sources(groups)
    items, errors = fetch_all(sources)
    write_jsonl(out / "00-pulled.jsonl", items)      # large; the template .gitignore leaves it out
    write_csv(out / "00-errors.csv", errors, ["group", "name", "url", "error", "detail"])

    unique, dupes = dedupe(items)
    write_jsonl(out / "01-unique.jsonl", unique)     # large, ignored as well
    write_csv(out / "01-duplicates.csv", dupes, ["title", "source", "merged_into", "key"])

    passed, dropped = hard_filters(unique, load_seen(date))
    write_jsonl(out / "02-passed.jsonl", passed)

    # invariant: 02-dropped.csv exists so a bad filter rule becomes visible, and an item that is
    # simply older than the window is not a rule worth reviewing. Age drops are counted in the
    # manifest instead; logging them made the file a megabyte a day of noise.
    write_csv(out / "02-dropped.csv", [d for d in dropped if d["reason"] != "too-old"],
              ["reason", "group", "source", "title", "url", "published"])

    kept = []
    if SEEN.exists():
        with SEEN.open(encoding="utf-8", newline="") as f:
            kept = [r for r in csv.DictReader(f) if r.get("date") != date]
    write_csv(SEEN, kept + [{"key": it["guid"] or it["url"], "date": date} for it in passed], ["key", "date"])

    by_reason = collections.Counter(d["reason"] for d in dropped)
    per_group = collections.Counter(it["group"] for it in passed)
    manifest = {
        "date": date, "groups": sorted(groups) if groups else ["all"],
        "feeds": len(sources), "feed_errors": len(errors),
        "pulled": len(items), "unique": len(unique), "duplicates": len(dupes),
        "passed": len(passed), "dropped": len(dropped),
        "dropped_by_reason": dict(by_reason.most_common()),
        "passed_per_group": dict(per_group.most_common()),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def _check() -> None:
    """The parts that can be wrong without anyone noticing."""
    import tempfile
    a = {"guid": "g1", "url": "u1", "title": "Model four is out", "source": "A"}
    b = {"guid": "g2", "url": "u2", "title": "Model four  IS   out!", "source": "B"}
    c = {"guid": "g1", "url": "uX", "title": "something else", "source": "C"}
    uniq, dupes = dedupe([a, b, c])
    assert len(uniq) == 1 and uniq[0]["confirmations"] == ["A", "B", "C"] and len(dupes) == 2, uniq
    assert len(dedupe([a, {"guid": "g9", "url": "u9", "title": "other news", "source": "D"}])[0]) == 2

    old = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS + 1)
    fresh = datetime.now(timezone.utc) - timedelta(hours=1)
    rows = [{"guid": "k1", "url": "u1", "title": "old", "published": old.isoformat()},
            {"guid": "k2", "url": "u2", "title": "fresh", "published": fresh.isoformat()},
            {"guid": "k3", "url": "u3", "title": "seen", "published": fresh.isoformat()},
            {"guid": "k4", "url": "", "title": "no url", "published": fresh.isoformat()}]
    passed, dropped = hard_filters(rows, {"k3"})
    assert [p["title"] for p in passed] == ["fresh"], passed
    assert {d["reason"] for d in dropped} == {"too-old", "already-seen", "no-url"}

    with tempfile.TemporaryDirectory() as td:
        seen = os.path.join(td, "seen.csv")
        open(seen, "w").write("key,date\nyesterday,2026-01-01\ntoday,2026-01-02\n")
        assert load_seen("2026-01-02", seen) == {"yesterday"}       # running a day again does not eat itself
        assert load_seen("2026-01-03", seen) == {"yesterday", "today"}
        feeds, ch = os.path.join(td, "feeds.csv"), os.path.join(td, "channels.csv")
        open(feeds, "w").write("group,name,url,status\na,A,https://a.example/feed,\nb,B,https://b.example/feed,off\n"
                               "c,C,https://c.example/search?q=<term>,\n")
        open(ch, "w").write("group,channel,channel_id\na,Chan,UC123\n")
        got = read_sources(None, feeds, ch)
        assert [s["group"] for s in got] == ["a", "youtube-a"], got   # off and template rows are skipped
        assert read_sources({"a"}, feeds, ch) == got[:1]

    assert is_reddit("https://www.reddit.com/r/x/top/.rss?t=week") and not is_reddit("https://example.com/feed/")
    print("ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--group", help="groups from feeds.csv, comma separated")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        _check()
        sys.exit(0)
    if not FEEDS.exists():
        print("no sources: _config/feed/feeds.csv is missing; see core/workflows/feed/setup.md")
        sys.exit(1)
    print(json.dumps(run(args.group, args.date), ensure_ascii=False, indent=2))
