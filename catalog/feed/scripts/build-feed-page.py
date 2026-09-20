#!/usr/bin/env python3
"""Build the feed page: the template plus one day of cards from the ICM.

    build-feed-page.py [<data>/<date>.json]    # default: the newest day; writes `out`
    build-feed-page.py --publish [day]         # the page without its own head, plus the connector manifest
    build-feed-page.py --preview [day]         # with a fake `db`: open it and read window.__writes
    build-feed-page.py --stale [day]           # which rows have sources that changed since the last build
    build-feed-page.py --same <a.html> <b.html>  # do two built pages carry the same feed
    build-feed-page.py --check

invariant: cards are NOT written into HTML but into <data>/<date>.json, and every story carries
`source`. A card without a source does not enter: a feed that is flicked through fast is the
easiest way for an unsupported number to slip into the ICM as a fact, so the check stands here
and not in the head of whoever writes the cards.
invariant: nothing about the owner is in this file. Labels, the table of hosts, the catalog of
actions, paths and thresholds come from _config/; without them the page is in English.
"""
import glob
import hashlib
import html
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, config, data, image_size, media_path, video_size

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = "template/feed-template.html"
VIDEO = (".mp4", ".webm", ".mov")
LABELS = {
    "title": "Daily feed", "comment": "Comment", "commentShort": "comment",
    "commentPlaceholder": "What works and what does not. Written rarely, so it counts the most.",
    "thumbUp": "thumb up", "thumbDown": "thumb down", "save": "Save", "cancel": "Cancel", "saved": "saved",
    "close": "Close", "details": "details", "like": "like", "swipe": "swipe",
    "previousCard": "previous card", "nextCard": "next card", "toTop": "Back to top",
    "open": "Open", "openOn": "Open on {host}",
    "endTitle": "That is all for today",
    "endBody": "What you looked at and what you liked is written down, and tomorrow's feed follows it.",
    "rows": {"one": "row", "other": "rows"}, "cards": {"one": "card", "other": "cards"}, "liked": "liked",
}
# Fields that are not components but carry the story or the cover itself.
CARRIERS = {"title", "eyebrow", "unit", "label", "subtitle", "tone", "video", "metricVariant",
            "listVariant", "id", "cover", "stories", "defaults", "image"}


def _lib_dir():
    lib = os.environ.get("ICM_LIB") or os.path.join(ROOT, "core/ui")
    if not os.path.exists(os.path.join(lib, "build.py")):
        sys.exit("the component library is not at %s; run install.sh again or set ICM_LIB" % lib)
    return lib


def _lib():
    spec = importlib.util.spec_from_file_location("icmlib", os.path.join(_lib_dir(), "build.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def schema():
    return json.load(open(os.path.join(_lib_dir(), "schema.json"), encoding="utf-8"))


def catalog(cfg):
    """The owner's catalog of actions; the library ships an English default."""
    own = os.path.join(ROOT, cfg["actions"])
    path = own if os.path.exists(own) else os.path.join(_lib_dir(), "actions.json")
    return json.load(open(path, encoding="utf-8"))["actions"]


def cards(feed):
    """(where, card, is_cover) for every screen of the feed."""
    for row in feed.get("rows") or []:
        rid = row.get("id") or "?"
        yield "row '%s' cover" % rid, row.get("cover") or {}, True
        for i, st in enumerate(row.get("stories") or []):
            yield "row '%s' story %d" % (rid, i), st, False


def check_actions(feed, cat):
    """An action must exist in the catalog and have everything its input asks for.

    invariant: the agent can NOT compose a call. `(server, tool)` has to be in the manifest that
    is declared when the page is published, so a call outside the catalog fails only on the
    owner's phone. So it fails here, at build time.
    """
    errors = []
    for where, card, _ in cards(feed):
        for a in card.get("actions") or []:
            d = cat.get(a.get("id"))
            if not d:
                errors.append("%s: unknown action '%s'" % (where, a.get("id")))
                continue
            need = set(re.findall(r"\{\{(\w+)\}\}", json.dumps(d))) | set(d.get("params") or {})
            missing = need - set(a.get("params") or {})
            if missing:
                errors.append("%s: action '%s' lacks %s" % (where, a["id"], ", ".join(sorted(missing))))
    assert not errors, "actions: " + "; ".join(errors[:6])


def manifest(feed, cat):
    """The connectors the feed REALLY uses, computed from the actions on its cards. A manifest
    written by hand drifts from the content as soon as someone adds an action."""
    tools = {}
    for _, card, _ in cards(feed):
        for a in card.get("actions") or []:
            d = cat.get(a.get("id")) or {}
            if d.get("kind") == "mcp":
                tools.setdefault(d["server"], set()).add(d["tool"])
    return [{"server": k, "tools": sorted(v)} for k, v in sorted(tools.items())]


def check_schema(feed, sch):
    """Fails on an unknown field, an unknown variant or a limit exceeded. The schema is the
    source of truth for both the agent and the code, so they cannot drift."""
    comp = sch["components"]
    allowed = set(comp) | CARRIERS
    errors = []
    for where, card, _ in cards(feed):
        errors += ["%s: unknown field '%s'" % (where, k) for k in card if k not in allowed]
        for name, d in comp.items():
            if name not in card:
                continue
            v = d.get("variants")
            if v:
                # the variant sits inside the component's own object (`series.kind`, `delta.direction`)
                # or beside it on the card (`listVariant`, `metricVariant`)
                prop, val = v["_prop"], None
                if isinstance(card[name], dict):
                    val = card[name].get(prop, card[name].get("kind") if prop == "variant" else None)
                if val is None:
                    val = card.get(name + "Variant")
                if val is not None and val not in v["values"]:
                    errors.append("%s: %s.%s = '%s', allowed %s" % (where, name, prop, val, "/".join(v["values"])))
            lim = d.get("limits") or {}
            if "chars" in lim and isinstance(card[name], str) and len(card[name]) > lim["chars"]:
                errors.append("%s: %s is longer than %d characters" % (where, name, lim["chars"]))
            if "items" in lim and isinstance(card[name], list) and len(card[name]) > lim["items"]:
                errors.append("%s: %s has more than %d items" % (where, name, lim["items"]))
            if "values" in lim and isinstance(card[name], dict) and len(card[name].get("values") or []) > lim["values"]:
                errors.append("%s: %s has more than %d values" % (where, name, lim["values"]))
        for i, t in enumerate(card.get("tags") or []):
            kind = t.get("kind") if isinstance(t, dict) else None
            if kind is not None and kind not in comp["tags"]["variants"]["values"]:
                errors.append("%s: tags[%d].kind = '%s', allowed %s" % (where, i, kind, "/".join(comp["tags"]["variants"]["values"])))
    assert not errors, "schema: " + "; ".join(errors[:6])


# Rules that hold the layout, and the script that carries the diary. A selector that matches
# nothing is not reported by CSS, and a renamed field leaves a page that still works, only
# silently, without a single write: the fault shows tomorrow, when there is nothing to read.
HOLDS_CSS = (".story.cover{", ".cover h2{", ".cover .subtitle{", ".cover .eyebrow{", ".story{", ".track{",
             ".front{", ".media{", ".details{", ".story::after{", ".front,.details{will-change:", ".layer{",
             ".hint{", "#end .story{", "#bar{", "#steps{")
HOLDS = ("icmHost.use('db')", "/*ICM-HOST*/", "/*ICM-CSS*/", "/*ICM-JS*/", "/*FEED-DATA*/", "icm-metric", "icm-facts", "icm-button",
         "const cardActions", "feed.addEventListener('icm-action'", "feed.addEventListener('icm-answer'",
         "/^(tel|sms):/i.test(t)",          # without it `+` in a number becomes %2B and the call fails
         "clip-path:inset(0)",              # a compositing layer ignores overflow:hidden on iOS
         "G.timeline()", "c.doc('diary/' + (D.day || D.date))", 'data-do="like"', "data-key=")


def check_template(t):
    style = t[t.index("<style>"):t.index("</style>")]
    for sel in HOLDS_CSS:
        assert sel in style, "the style has no rule for %s" % sel.rstrip("{")
    for code in HOLDS:
        assert code in t, "the template no longer contains %s" % code


def source_path(src):
    """The path in the ICM a source points at, or None when it points outside. A source is a
    bare path, or {kind, path, id, url}; a card that came from a feed has no path at all."""
    return src if isinstance(src, str) else src.get("path") if isinstance(src, dict) else None


def source_name(src):
    if isinstance(src, dict):
        return src.get("path") or src.get("url") or src.get("id") or src.get("kind") or ""
    return src or ""


def check(feed, root=None, media=None):
    """Fails loudly instead of building a feed with an unsupported number. Returns the story count."""
    root, media = root or ROOT, media or media_path
    assert feed.get("rows"), "the feed has no rows; an empty day is one row that says so"

    def media_exists(rel, where):
        # invariant: the path must be RELATIVE, because the page asks for `media/<file>`. With an
        # absolute one the check passes for a file that exists on this machine and not beside
        # the page: a whole feed was published without one image and no test failed.
        assert not os.path.isabs(rel), "%s: media must be a relative path, got %s" % (where, rel)
        assert os.path.exists(media(rel)), "%s: media does not exist: %s" % (where, rel)

    total = 0
    for row in feed["rows"]:
        assert row.get("stories"), "row '%s' has no stories" % (row.get("id") or "?")
        total += len(row["stories"])
    for where, c, cover in cards(feed):
        for need in (("title", "subtitle") if cover else ("hook", "source")):
            assert c.get(need), "%s has no %s" % (where, need)
        if not cover:
            assert c.get("body") or c.get("facts"), "%s has neither body nor facts" % where
        sp = source_path(c.get("source"))
        assert sp is None or os.path.exists(os.path.join(root, sp)), "%s: source does not exist: %s" % (where, sp)
        if c.get("metric") not in (None, ""):
            assert c.get("label"), "%s has a metric without a label" % where
        if c.get("media"):
            media_exists(c["media"], where)
        if c.get("video"):
            assert cover, "%s: only a cover carries video" % where
            assert c["video"].lower().endswith(VIDEO), "%s: video is not a video file: %s" % (where, c["video"])
            media_exists(c["video"], where + " video")
        for l in c.get("links") or []:
            assert str(l.get("href", "")).startswith("http"), "%s: a link is not an http address" % where
    return total


def expand(feed):
    """Push `row.defaults` down into every story, before checking and building. The same pair
    repeated on fifteen stories is fifteen rows the agent must write; the page knows nothing of it."""
    for row in feed.get("rows") or []:
        for st in (row.get("stories") or []) if row.get("defaults") else []:
            for k, v in row["defaults"].items():
                if k == "facts":
                    st["facts"] = (st.get("facts") or []) + [list(x) for x in v]   # general pairs go AFTER its own
                elif k not in st:
                    st[k] = v
        row.pop("defaults", None)
    return feed


def prints(feed, root=None):
    """Fingerprint of the sources per row: what the agent had to read to write it. Reading is
    most of the cost of a feed, so next time what did not change is not read again."""
    out = {}
    for row in feed.get("rows") or []:
        paths = {source_name(c.get("source")) for c in [row.get("cover") or {}] + list(row.get("stories") or [])} - {""}
        h = hashlib.sha256()
        for rel in sorted(paths):
            h.update(rel.encode("utf-8"))
            p = os.path.join(root or ROOT, rel)
            if os.path.isfile(p):
                h.update(open(p, "rb").read())
        out[row["id"]] = h.hexdigest()[:16]
    return out


def page_print(feed, pr):
    """One fingerprint of the whole page: which rows, in which order, from which sources.

    The attention diary is written with this number, so tomorrow it is mechanically known whether
    it measured the page that was published. Without it a diary from a superseded page of the
    same day reads like evidence, and thresholds get moved on it.
    """
    h = hashlib.sha256((feed.get("day") or feed.get("date") or "").encode("utf-8"))
    for row in feed.get("rows") or []:
        h.update(b"\x00" + row["id"].encode("utf-8") + str(len(row.get("stories") or [])).encode() + (pr.get(row["id"]) or "").encode())
    return h.hexdigest()[:12]


def _words(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.replace("x", " ").split()
    except FileNotFoundError:
        return []


def ratios(feed, media=None):
    """Aspect ratio of every media file, computed HERE and not in the browser: there it would be
    known only after the image loads, and the card would jump. The header readers come first
    (common.py); external tools are a fallback for formats they do not know."""
    media = media or media_path
    out = {}
    for rel in sorted({c.get(k) for _, c, _ in cards(feed) for k in ("media", "video")} - {None, ""}):
        p = media(rel)
        if rel.lower().endswith(VIDEO):
            m = video_size(p) or _words(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                         "stream=width,height", "-of", "csv=p=0:s=x", p])
        else:
            m = image_size(p) or _words(["magick", "identify", "-format", "%w %h", p]) or _words(["identify", "-format", "%w %h", p])
        if m and len(m) == 2 and int(m[1]):
            out[rel] = round(int(m[0]) / int(m[1]), 4)
    return out


def same_image(feed, media=None):
    """invariant: one image file under several names fails the build. It is how a placeholder
    passes for content: four cards of a row each "have media", and it is one picture."""
    media, seen = media or media_path, {}
    for rel in sorted({c["media"] for _, c, _ in cards(feed) if c.get("media")}):
        seen.setdefault(hashlib.md5(open(media(rel), "rb").read()).hexdigest(), []).append(rel)
    dup = [v for v in seen.values() if len(v) > 1]
    assert not dup, "the same image under several names: %s. Keep one, on the cover, and let the cards fall back to it." % dup


def bare(feed):
    """Screens that will show no image: no media of their own and none on the cover of their row."""
    out = []
    for row in feed.get("rows") or []:
        c = row.get("cover") or {}
        if not (c.get("media") or c.get("video")):
            out += ["%s#%d" % (row["id"], i) for i, x in enumerate([c] + list(row.get("stories") or [])) if not x.get("media")]
    return out


def template(cfg, L):
    own = os.path.join(ROOT, "_config/overrides/core/workflows/feed", TEMPLATE)
    t = open(own if os.path.exists(own) else os.path.join(HERE, TEMPLATE), encoding="utf-8").read()
    check_template(t)
    for k, v in L.items():
        if isinstance(v, str):
            t = t.replace("{{%s}}" % k, html.escape(v))
    left = re.findall(r"\{\{(?!url\}\})\w+\}\}", t.split("<script>")[0])
    assert not left, "template tokens without a label: %s" % sorted(set(left))
    return t


def labels(cfg):
    L = {"locale": "en", **LABELS}
    shared = os.path.join(ROOT, "_config/labels.json")
    if os.path.exists(shared):
        L["locale"] = json.load(open(shared, encoding="utf-8")).get("locale", "en")
    return {**L, **cfg["labels"]}


def assemble(feed, day, cfg, media=None):
    """The page data: the feed plus everything the page needs and must not compute itself."""
    cat = catalog(cfg)
    if "reels" in feed and "rows" not in feed:   # ponytail: days written before 0.5.0 called a row a reel; drop when none are built any more
        feed["rows"] = feed.pop("reels")
    feed = expand(feed)
    for row in feed.get("rows") or []:           # the standing cover of a row, when the day brings none
        c = row.get("cover") or {}
        if not (c.get("media") or c.get("video")) and cfg["covers"].get(row.get("id")):
            c["media"] = cfg["covers"][row["id"]]
    feed.pop("prints", None)
    check_schema(feed, schema())
    total = check(feed, media=media)
    check_actions(feed, cat)
    pr = prints(feed)
    feed["ratios"] = ratios(feed, media)
    # invariant: EVERY media file gets a ratio. The page picks full screen or a frame by it, so a
    # file without one silently gets the wrong frame.
    unmeasured = sorted({c.get(k) for _, c, _ in cards(feed) for k in ("media", "video")} - {None, ""} - set(feed["ratios"]))
    same_image(feed, media)
    assert not unmeasured, "no size for: %s. The header reader does not know the format and no external tool is here (imagemagick, ffmpeg)." % ", ".join(unmeasured)
    # `date` is for reading ("18 September 2026"); a document path in `db` takes only letters,
    # digits and _ - . ~ : @ +, so the day goes separately, from the file name.
    assert re.fullmatch(r"[\w.~:@+-]+", day), "the file name cannot be a document id: %s" % day
    feed.update({"day": day, "actions": cat, "labels": labels(cfg), "hosts": cfg["hosts"], "seenMs": cfg["seen_ms"]})
    feed.setdefault("date", day)
    feed["build"] = page_print(feed, pr)
    return feed, pr, total


def render(feed, cfg):
    t = _lib().inline(template(cfg, feed["labels"]))
    js = json.dumps(feed, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")   # </ would close the script early
    # The adapter's page side: how this host hands a page its store and connectors.
    hosts = sorted(glob.glob(os.path.join(ROOT, "core/adapters/*/page-host.js")))
    host = open(hosts[0], encoding="utf-8").read() if hosts else ""
    return t.replace("/*ICM-HOST*/", host).replace("/*FEED-DATA*/", js)


def _parts(path):
    s = open(path, encoding="utf-8").read()
    m = re.search(r'<script id="feed-data" type="application/json">(.*?)</script>', s, re.S)
    assert m, "no data block in %s" % path
    return json.loads(m.group(1).replace("<\\/", "</")), s[:m.start(1)] + s[m.end(1):]


def same(a, b):
    """Do two built pages give THE SAME feed, whatever the order of keys. It proves an
    optimization instead of claiming it; comparing bytes is wrong, because moving a field in the
    data changes bytes and nothing anyone sees."""
    (da, ta), (db, tb) = _parts(a), _parts(b)
    return ta == tb and json.dumps(da, sort_keys=True) == json.dumps(db, sort_keys=True)


# A fake `db`. The page writes its diary into window.__writes instead of the cloud, so the
# behaviour shows in a browser; the path goes through the same rule as the real store, because
# that is exactly where a fault was once (a date for reading used as a document id).
STUB = r"""<script>
window.__writes = [];
window.__seed = null;   // put a document body here to try merging on reopening
window.icmHost = { use: async n => n !== 'db' ? null : ({
  doc: p => { if (!/^[\w.~:@+-]+(\/[\w.~:@+-]+)*$/.test(p) || p.split('/').length % 2)
                throw new TypeError('bad path: ' + p);
    return { path: p,
      get: async () => ({exists: !!window.__seed, data: () => window.__seed}),
      set: async t => { window.__writes.push(JSON.parse(JSON.stringify(t))); } }; }
}) };
</script>
"""
MARK = '<script id="feed-data"'   # the stub lands after the adapter's host script, so it wins


def main(flags, args):
    if "--same" in flags:
        ok = same(args[0], args[1])
        print("the feed is %s" % ("the same" if ok else "DIFFERENT"))
        return 0 if ok else 1
    cfg = config()
    days = sorted(glob.glob(data("[0-9]*.json")))
    if not args and not days:
        print("0 days: nothing in %s; SKILL.md says how a day is written" % os.path.relpath(data(), ROOT))
        return 1
    path = args[0] if args else days[-1]
    raw = json.load(open(path, encoding="utf-8"))
    old = raw.get("prints")
    feed, pr, total = assemble(json.loads(json.dumps(raw)), os.path.splitext(os.path.basename(path))[0], cfg)
    if "--stale" in flags:
        changed = [k for k, v in pr.items() if not old or old.get(k) != v]
        print("stale: " + (", ".join(changed) if changed else "no row"))
        return 0
    page = render(feed, cfg)
    out = os.path.join(ROOT, cfg["out"])
    if "--preview" in flags:
        assert MARK in page
        page, out = page.replace(MARK, STUB + MARK, 1), out.replace(".html", "-preview.html")
    if "--publish" in flags:
        # A host that wraps the file in its own document wants ours without a head; with it goes
        # the block that pads a page served on its own for the safe area.
        m = manifest(feed, feed["actions"])
        print("manifest: %s" % (json.dumps(m, ensure_ascii=False) if m else "no connector"))
        page = re.sub(r"\n/\* A page served on its own.*?\n:root\{padding-top[^}]*\}", "", page[page.index("<title>"):], flags=re.S)
        assert ":root{padding-top" not in page and "safe-area" in page, "the fixed bars must keep env(safe-area-inset)"
        out = out.replace(".html", "-publish.html")
        files = {rel: os.path.relpath(media_path(rel), ROOT) for rel in sorted(feed["ratios"])}
        open(out.replace(".html", ".files.json"), "w", encoding="utf-8").write(json.dumps(files, indent=1))
        print("files: %d media files to publish beside the page, listed in %s" % (len(files), os.path.relpath(out.replace(".html", ".files.json"), ROOT)))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    # The fingerprints go back into the day's data, so next time knows what is new, and `build`
    # with them: the diary is compared against the page that was published that day.
    # invariant: this is why an unknown flag stops the run instead of being ignored.
    raw["prints"], raw["build"] = pr, feed["build"]
    open(path, "w", encoding="utf-8").write(json.dumps(raw, ensure_ascii=False, indent=1))
    b = bare(feed)
    print("bare: %s" % (("%d screens without an image: %s" % (len(b), ", ".join(b[:12]))) if b else "every screen has an image"))
    print("wrote %s, %d B, %d rows, %d stories, %d screens; media beside it: %s/"
          % (os.path.relpath(out, ROOT), os.path.getsize(out), len(feed["rows"]), total, total + len(feed["rows"]) + 1, cfg["media_dir"]))
    return 0


def _check():
    import tempfile
    tmp = tempfile.mkdtemp()
    png = lambda w, h: b"\x89PNG\r\n\x1a\n" + b"\0\0\0\rIHDR" + w.to_bytes(4, "big") + h.to_bytes(4, "big") + b"\0" * 8
    open(os.path.join(tmp, "a.png"), "wb").write(png(1200, 800))
    open(os.path.join(tmp, "src.md"), "w").write("x")
    media = lambda rel: os.path.join(tmp, rel.split("/", 1)[1])
    sch = schema()
    st = {"hook": "h", "body": "b", "source": "src.md"}
    cover = {"title": "A", "subtitle": "s", "media": "media/a.png"}

    def feed(**kw):
        return {"rows": [dict({"id": "a", "cover": dict(cover), "stories": [dict(st)]}, **kw)]}

    assert check(feed(stories=[st, dict(st)]), tmp, media) == 2
    assert check(feed(cover={"title": "A", "subtitle": "s"}), tmp, media) == 1, "a cover without media must pass"
    assert check(feed(stories=[dict(st, source={"kind": "feed", "url": "https://example.com/x"})]), tmp, media) == 1
    # invariant: every bad feed must fail with ITS OWN message. A check that only asserts
    # "something failed" once passed for months on the wrong reason (a renamed field tripped the
    # schema first), and the rules it was named for were never exercised.
    for bad, why in [
        ({"rows": []}, "no rows"),
        (feed(stories=[]), "has no stories"),
        (feed(cover=dict(cover, media="media/none.png")), "media does not exist"),
        (feed(cover=dict(cover, media=os.path.join(tmp, "a.png"))), "must be a relative path"),
        (feed(stories=[dict(st, nonsense="x")]), "unknown field 'nonsense'"),
        (feed(stories=[dict(st, list=["a"], listVariant="stars")]), "list.variant = 'stars'"),
        (feed(stories=[dict(st, tags=[{"text": "x", "kind": "pink"}])]), "tags[0].kind = 'pink'"),
        (feed(stories=[dict(st, list=["a"] * 9)]), "list has more than"),
        (feed(cover=dict(cover, video="media/none.mp4")), "media does not exist"),
        (feed(cover=dict(cover, video="media/a.png")), "video is not a video file"),
        (feed(stories=[dict(st, video="media/a.mp4")]), "only a cover carries video"),
        (feed(cover=dict(cover, subtitle="")), "cover has no subtitle"),
        (feed(cover=dict(cover, metric="5")), "metric without a label"),
        (feed(stories=[dict(st, source="none.md")]), "source does not exist"),
        (feed(stories=[dict(st, hook="")]), "has no hook"),
        (feed(stories=[dict(st, hook="x" * 81)]), "hook is longer than 80"),
        (feed(stories=[{"hook": "h", "source": "src.md"}]), "neither body nor facts"),
        (feed(stories=[dict(st, links=[{"href": "domains/x.md", "label": "x"}])]), "not an http address"),
    ]:
        try:
            check_schema(bad, sch)
            check(bad, tmp, media)
        except AssertionError as e:
            assert why in str(e), "failed for the wrong reason: wanted '%s', got '%s'" % (why, e)
            continue
        raise AssertionError("passed and must not: " + why)

    # the example day in the docs is a real day: it cannot drift from the schema or the rules
    ex = json.load(open(os.path.join(HERE, "template/example-day.json"), encoding="utf-8"))
    os.makedirs(os.path.join(tmp, "domains/garden/output"))
    open(os.path.join(tmp, "domains/garden/output/greenhouse-plan.md"), "w").write("x")
    check_schema(expand(ex), sch)
    assert check(ex, tmp, media) == 3

    cat = {"open": {"kind": "link", "href": "{{url}}", "label": "Open"}, "file": {"kind": "mcp", "server": "s", "tool": "t", "input": {"q": "{{id}}"}, "label": "File"}}
    good = feed(stories=[dict(st, actions=[{"id": "file", "params": {"id": "1"}}, {"id": "open", "params": {"url": "https://x"}}])])
    check_actions(good, cat)
    assert manifest(good, cat) == [{"server": "s", "tools": ["t"]}]
    for bad, why in [(feed(stories=[dict(st, actions=[{"id": "nope"}])]), "unknown action"),
                     (feed(stories=[dict(st, actions=[{"id": "file"}])]), "lacks id")]:
        try:
            check_actions(bad, cat)
        except AssertionError as e:
            assert why in str(e), e
        else:
            raise AssertionError("passed and must not: " + why)

    f = expand({"rows": [{"id": "a", "defaults": {"source": "src.md", "facts": [["S", "v"]]},
                           "stories": [{"hook": "h", "facts": [["own", "1"]]}, {"hook": "h", "source": "other.md"}]}]})
    s0, s1 = f["rows"][0]["stories"]
    assert s0["source"] == "src.md" and s0["facts"] == [["own", "1"], ["S", "v"]] and s1["source"] == "other.md" and "defaults" not in f["rows"][0]

    open(os.path.join(tmp, "b.png"), "wb").write(png(1200, 800))
    try:
        same_image(feed(stories=[dict(st, media="media/b.png")]), media)
    except AssertionError as e:
        assert "several names" in str(e)
    else:
        raise AssertionError("one picture under two names passed")
    assert bare(feed(cover={"title": "A", "subtitle": "s"})) == ["a#0", "a#1"] and not bare(feed())

    g = feed()
    assert ratios(g, media) == {"media/a.png": 1.5}
    p1 = prints(g, tmp)
    open(os.path.join(tmp, "src.md"), "w").write("changed")
    assert prints(g, tmp) != p1, "a changed source must change the print"
    assert page_print(g, p1) != page_print(feed(stories=[st, dict(st)]), p1)

    cfg = config()
    t = template({**cfg}, {"locale": "en", **LABELS})
    assert "{{title}}" not in t and "<title>Daily feed</title>" in t
    broken = open(os.path.join(HERE, TEMPLATE), encoding="utf-8").read().replace(".story.cover{", ".row .cover .story{")
    try:
        check_template(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError("a broken selector passed")
    # the whole page, and the stub lands where the page reads it
    g.update({"labels": {"locale": "en", **LABELS}, "day": "2026-01-02"})
    page = render(g, cfg)
    assert MARK in page and "/*ICM-JS*/" not in page and "/*FEED-DATA*/" not in page
    a, b = os.path.join(tmp, "a.html"), os.path.join(tmp, "b.html")
    open(a, "w", encoding="utf-8").write(page)
    g2 = json.loads(json.dumps(g)); g2["rows"][0] = dict(reversed(list(g2["rows"][0].items())))
    open(b, "w", encoding="utf-8").write(render(g2, cfg))
    assert same(a, b), "key order must not matter"
    g2["rows"][0]["stories"][0]["hook"] = "other"
    open(b, "w", encoding="utf-8").write(render(g2, cfg))
    assert not same(a, b)
    print("ok")


FLAGS = {"--same", "--stale", "--preview", "--publish", "--check"}

if __name__ == "__main__":
    # invariant: an unknown flag stops the run. A build rewrites `prints` in the day's data file,
    # so a flag that is silently ignored changes data nobody asked to change.
    flags = [a for a in sys.argv[1:] if a.startswith("-")]
    unknown = [a for a in flags if a not in FLAGS]
    if unknown:
        print(__doc__ if unknown == ["--help"] else "unknown flag: %s; known: %s" % (" ".join(unknown), " ".join(sorted(FLAGS))))
        sys.exit(0 if unknown == ["--help"] else 2)
    sys.exit(_check() or 0) if "--check" in flags else sys.exit(main(flags, [a for a in sys.argv[1:] if not a.startswith("-")]))
