#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["youtube-transcript-api>=1.0", "trafilatura>=2.0"]
# ///
"""Step 2.5 of the funnel: read what a signal actually says, before anything judges it.

A card does not enter the feed until its source has been read. The point is not prettier copy:
without the content there is no way to tell whether an item belongs in the feed at all, so this
runs BEFORE scoring, not after it.

    uv run read-sources.py                 # today
    uv run read-sources.py --date 2026-01-02 --limit 40
    uv run read-sources.py --check         # self-check, no network, touches nothing

Reads <data>/signals/<date>/02-passed.jsonl, writes 025-read.jsonl and 025-unread.csv beside it.
Every item that is not read carries a reason, because a silent gap here shrinks the feed and
nobody would know why.
"""
import argparse, csv, json, os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import config, data

CFG = config()
BASE = Path(data("signals"))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
MAX_CHARS = CFG["max_chars"]

# invariant: measured on 2026-09-19, not assumed, and it will rot: recipes/any-reader.md says how
# to measure again. Anonymous reddit answers ONE request and then sets x-ratelimit-remaining to 0
# with a ~60 s reset. Everything else is unmetered, so only reddit gets a bucket and a budget.
REDDIT_GAP, REDDIT_BUDGET = CFG["reddit_gap"], CFG["reddit_budget"]

# invariant: YouTube blocks the whole IP, not the request, and the block OUTLASTS the run
# (measured 2026-09-19: 30 transcripts were fine, 42 produced IpBlocked, and a later run with a
# short gap had 40 of 42 blocked because the IP was already cold). Pacing alone cannot undo an
# active block, so there are three defences, in order:
#   1. a real gap, not a token one
#   2. a daily budget, because the ceiling is per IP per day, not per burst
#   3. a breaker: after BREAKER_AT consecutive blocks, stop asking for the rest of the run
YOUTUBE_GAP, YOUTUBE_BUDGET, BREAKER_AT = CFG["youtube_gap"], CFG["youtube_budget"], CFG["breaker_at"]


def kind_of(url: str) -> str:
    h = (urlparse(url).hostname or "").lower()
    if "youtube.com" in h or "youtu.be" in h:
        return "youtube"
    if "reddit.com" in h:
        return "reddit"
    if h.startswith("forum.") or "/t/" in url:
        return "discourse"
    return "article"


def video_id(url: str):
    # invariant: /shorts/ and /live/ carry transcripts like any other video; matching only ?v=
    # and youtu.be skipped a third of the items as "not a video".
    for pat in (r"[?&]v=([A-Za-z0-9_-]{11})", r"youtu\.be/([A-Za-z0-9_-]{11})",
                r"/shorts/([A-Za-z0-9_-]{11})", r"/live/([A-Za-z0-9_-]{11})", r"/embed/([A-Za-z0-9_-]{11})"):
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def strip_html(s: str) -> str:
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def fetch_bytes(url: str, timeout: int = 25) -> bytes:
    req = Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urlopen(req, timeout=timeout) as r:
        return r.read()


_yt_blocked = 0


def read_youtube(url: str):
    global _yt_blocked
    if _yt_blocked >= BREAKER_AT:
        return "", "transcript:breaker"
    vid = video_id(url)
    if not vid:
        return "", "not-a-video-url"
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception:
        # invariant: a cloud runner may predate any setup script, so a missing library is a
        # skipped item, never a dead run.
        return "", "library-missing"
    try:
        snippets = YouTubeTranscriptApi().fetch(vid)
    except Exception as exc:
        name = type(exc).__name__
        if "Block" in name or "TooManyRequests" in name:
            _yt_blocked += 1
        return "", "transcript:" + name
    _yt_blocked = 0
    text = " ".join(getattr(s, "text", "") for s in snippets).strip()
    return (text, "transcript") if text else ("", "transcript-empty")


def read_discourse(url: str):
    m = re.search(r"/t/(?:[^/]+/)?(\d+)", url)
    if not m:
        return "", "no-topic-id"
    root = f"{urlparse(url).scheme}://{urlparse(url).hostname}"
    try:
        d = json.loads(fetch_bytes(f"{root}/t/{m.group(1)}.json"))
    except Exception as exc:
        return "", "discourse:" + type(exc).__name__
    posts = (d.get("post_stream") or {}).get("posts") or []
    text = "\n\n".join(strip_html(p.get("cooked") or "") for p in posts[:20]).strip()
    return (text, "discourse") if text else ("", "discourse-empty")


def read_reddit(url: str):
    # .json answered 403 in every variant when measured; .rss is the surface that answers, and it
    # carries the post body plus the top comments.
    try:
        raw = fetch_bytes(url.rstrip("/") + "/.rss?sort=top&limit=5").decode("utf-8", "replace")
    except Exception as exc:
        return "", "reddit:" + type(exc).__name__
    text = "\n\n".join(strip_html(b) for b in re.findall(r"(?s)<content[^>]*>(.*?)</content>", raw)).strip()
    return (text, "reddit-rss") if text else ("", "reddit-empty")


def read_article(url: str):
    try:
        html = fetch_bytes(url).decode("utf-8", "replace")
    except Exception as exc:
        return "", "http:" + type(exc).__name__
    # invariant: trafilatura's own downloader fails on some hosts where a plain request gets a
    # healthy 200, so it is always fed the body we already have.
    try:
        import trafilatura
        text = trafilatura.extract(html) or ""
    except Exception:
        text = ""
    if not text:
        text = strip_html(html)
    return (text.strip(), "trafilatura") if text.strip() else ("", "text-empty")


READERS = {"youtube": read_youtube, "discourse": read_discourse, "reddit": read_reddit, "article": read_article}


class Bucket:
    """One request per `gap` seconds, shared across threads."""

    def __init__(self, gap: float):
        self.gap, self.lock, self.last = gap, threading.Lock(), 0.0

    def take(self) -> None:
        with self.lock:
            wait = self.gap - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()


def read_one(it: dict, reader=None) -> tuple:
    """(read row, None) or (None, unread row)."""
    k = kind_of(it["url"])
    text, how = (reader or READERS[k])(it["url"])
    # invariant: a host behind a bot wall answers 403 to everything. The feed's own summary is
    # weaker than the page but far better than nothing, so it is used and MARKED as weaker.
    failed = ""
    if not text and len(it.get("summary") or "") > 200:
        # invariant: the fallback must not hide WHY the real read failed. Without
        # `failed_reason` the manifest once said "youtube: 42 read" on a day when almost all
        # were blocked and served from the feed summary: the metric looked healthy while the
        # thing it measures had stopped.
        failed, text, how = how, it["summary"], "feed-summary"
    if text:
        return {**it, "text": text[:MAX_CHARS], "text_source": how, "failed_reason": failed, "kind": k}, None
    return None, {"url": it["url"], "kind": k, "reason": how, "source": it["source"], "title": it["title"]}


def run(date: str, limit: int) -> dict:
    out = BASE / date
    items = [json.loads(l) for l in (out / "02-passed.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    by = {k: [it for it in items if kind_of(it["url"]) == k] for k in READERS}
    rest = by["article"] + by["discourse"]
    read, unread = [], []

    def keep(pair):
        (read if pair[0] else unread).append(pair[0] or pair[1])

    def over_budget(rows, kind):
        for it in rows:
            unread.append({"url": it["url"], "kind": kind, "reason": "budget", "source": it["source"], "title": it["title"]})

    with ThreadPoolExecutor(max_workers=8) as pool:
        for pair in pool.map(read_one, rest):
            keep(pair)
    # youtube and reddit each go through their own serial lane
    for rows, gap, budget, kind in ((by["youtube"], YOUTUBE_GAP, YOUTUBE_BUDGET, "youtube"),
                                    (by["reddit"], REDDIT_GAP, limit, "reddit")):
        b = Bucket(gap)
        for it in rows[:budget]:
            b.take()
            keep(read_one(it))
        over_budget(rows[budget:], kind)

    (out / "025-read.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in read), encoding="utf-8")
    with (out / "025-unread.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["reason", "kind", "source", "title", "url"], extrasaction="ignore")
        w.writeheader()
        w.writerows(unread)

    count = lambda rows, key: {k: sum(1 for r in rows if r.get(key) == k) for k in sorted({r.get(key) for r in rows if r.get(key)})}
    mf = out / "manifest.json"
    m = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    m.update({"read": len(read), "read_by_kind": count(read, "kind"), "read_by_source": count(read, "text_source"),
              "fallback_reason": count(read, "failed_reason"), "unread_by_reason": count(unread, "reason")})
    mf.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    return m


def _check() -> None:
    assert kind_of("https://www.youtube.com/watch?v=abc") == "youtube"
    assert kind_of("https://youtu.be/abcdefghijk") == "youtube"
    assert kind_of("https://www.reddit.com/r/x/comments/1/y/") == "reddit"
    assert kind_of("https://forum.example.com/t/something/7") == "discourse"
    assert kind_of("https://blog.example.com/2026/x/") == "article"

    assert video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1") == "dQw4w9WgXcQ"
    assert video_id("https://www.youtube.com/shorts/UyqSACHbrGE") == "UyqSACHbrGE"
    assert video_id("https://www.youtube.com/live/abcdefghijk") == "abcdefghijk"
    assert video_id("https://example.com/x") is None

    assert strip_html("<p>a &amp; b</p><script>x()</script>") == "a & b"

    t0 = time.time()
    b = Bucket(0.05)
    b.take(); b.take()
    assert time.time() - t0 >= 0.05, "the bucket must slow the second request down"

    global _yt_blocked
    _yt_blocked = BREAKER_AT
    assert read_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == ("", "transcript:breaker"), \
        "the breaker must stop further attempts instead of spending items on a wall"
    _yt_blocked = 0

    it = {"url": "https://blog.example.com/a", "source": "S", "title": "T", "summary": "x" * 300}
    got, _ = read_one(it, lambda u: ("", "http:HTTPError"))
    assert got["text_source"] == "feed-summary" and got["failed_reason"] == "http:HTTPError", "the fallback hid the failure"
    _, un = read_one({**it, "summary": "short"}, lambda u: ("", "http:HTTPError"))
    assert un["reason"] == "http:HTTPError"
    got, _ = read_one(it, lambda u: ("full text", "trafilatura"))
    assert got["text"] == "full text" and got["failed_reason"] == ""
    print("ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--limit", type=int, default=REDDIT_BUDGET, help="how many reddit threads")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        _check(); sys.exit(0)
    print(json.dumps(run(a.date, a.limit), ensure_ascii=False, indent=1))
