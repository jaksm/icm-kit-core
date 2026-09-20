#!/usr/bin/env python3
"""Fetch the real image or video behind a card and store it beside the page.

WHY THIS EXISTS, instead of <img src="https://...">: a published page usually runs under a
content security policy that blocks every image and video from another host, silently. A card
whose media points at someone else's URL is simply black. So media is fetched when the feed is
assembled and published as a file next to the page. A side benefit: the listing can vanish and
the card still works.

    fetch-media.py <page-url> <name> [--collage] [--width 1080]   # og:image of a page
    fetch-media.py <video-url> <name> --video [--seconds 6]
    fetch-media.py --fill <data>/<date>.json [--dry]              # every card without media
    fetch-media.py --check

Output is <media_dir>/<name>.webp (or .mp4) and the value for the card's `media` field, which is
always `media/<file>`: relative, because that is what the page asks for.

Needs ImageMagick (7 as `magick`, or 6 as `convert`) for images, yt-dlp and ffmpeg for video.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import config, image_size, media_path

CFG = config()
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/140 Safari/537.36"
OPENVERSE = "https://api.openverse.org/v1/images/"

# og:image is the only half reliable way to take the main image of an arbitrary page. It is looked
# for in both shapes, because the same tag also sits in the JSON a framework injects into the page.
OG = [re.compile(r'og:image["\\]*[^>]*?content=["\\]+(https://[^"\\ >]+)', re.I),
      re.compile(r'"og:image[^"]*"\s*,\s*"content"\s*:\s*"(https://[^"]+)"', re.I)]
IMAGE = re.compile(r'https://[^\s"\'<>\\]+\.(?:jpe?g|png|webp)(?:\?[^\s"\'<>\\]*)?', re.I)
# Logos, icons and site backgrounds are not the content of the page.
JUNK = re.compile(r'/(%s)/' % "|".join(["assets", "logos?", "icons?", "favicon", "backgrounds?", "placeholder", "sprite"]
                                       + [re.escape(w) for w in CFG["junk_paths"]]), re.I)


def _im(tool, *args):
    """Run ImageMagick: version 7 has one `magick` binary, version 6 has `convert` and `montage`."""
    if shutil.which("magick"):
        cmd = ["magick"] + ([] if tool == "convert" else [tool])
    else:
        assert shutil.which(tool), "ImageMagick is missing: neither `magick` nor `%s` is on the path" % tool
        cmd = [tool]
    subprocess.run(cmd + list(args), check=True)


def is_photo(path):
    """Does the download look like a photograph at all, not a logo or a banner.

    A filter on the URL does not catch everything: a site can serve its wordmark from the same
    host as its photos. A logo is small or stretched, a photograph is not, and that only shows
    after the download. The floor is low on purpose: real listings carry photos around 620x340.
    The site's logo returned as og:image for every page is caught by the ledger, not here.
    """
    w, h = image_size(path) or (0, 0)
    if not (w >= 400 and h >= 250 and 0.4 <= w / h <= 2.6):
        return False
    # ponytail: a wordmark on a flat ground passes the size test (seen 2026-09-20: a site's square
    # logo as og:image). Quantized to 256 colors at 200 px, photos kept 224 or more and the logo
    # 168. A naive threshold on ten samples; if it misjudges, measure again before moving it.
    try:
        tool = ["magick"] if shutil.which("magick") else ["convert"]
        k = subprocess.run(tool + [path, "-resize", "200x200", "-colors", "256", "-format", "%k", "info:"],
                           capture_output=True, text=True).stdout.strip()
        return not k.isdigit() or int(k) >= 200
    except FileNotFoundError:
        return True


def download(url, to):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        open(to, "wb").write(r.read())


def find_images(url, count=1):
    """Up to `count` image URLs from a page, og:image first."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        html = r.read().decode("utf-8", "replace")
    found = []
    for og in OG:
        m = og.search(html)
        if m:
            found.append(m.group(1))
            break
    if count > 1:
        # the rest from the same host as og:image: those are as a rule the photos of the
        # listing, while images from another host are ads and logos
        host = found[0].split("/")[2] if found else None
        for u in IMAGE.findall(html):
            if u in found or JUNK.search(u) or (host and u.split("/")[2] != host):
                continue
            found.append(u)
            if len(found) >= count:
                break
    return found[:count]


def _fit(src, w, h, out):
    _im("convert", src, "-resize", "%dx%d^" % (w, h), "-gravity", "center", "-extent", "%dx%d" % (w, h), out)
    return out


def store(inputs, name, width=None, collage=False):
    """One image -> webp at its own ratio. Several -> a contact strip on top plus a hero below.

    Why not 2x2: the card is a background under text and the curtain darkens it from below, so
    the lower half of a grid vanishes. The strip of small frames goes into the top third, where
    the curtain is lightest and the eye lands first.
    invariant: at most 4 images. A fifth gives frames narrower than 180 px on a phone.
    """
    width = width or CFG["image_width"]
    out = media_path("media/" + name + ".webp")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if collage and len(inputs) > 1:
        tmp = tempfile.mkdtemp()
        height = round(width * 16 / 9)
        hero, small = inputs[0], inputs[1:4]
        strip_h = round(height * 0.30)
        parts = [_fit(u, width // len(small), strip_h, os.path.join(tmp, "k%d.png" % i)) for i, u in enumerate(small)]
        strip = os.path.join(tmp, "strip.png")
        _im("montage", *parts, "-tile", "%dx1" % len(parts), "-geometry", "+0+0", strip)
        h = _fit(hero, width, height - strip_h, os.path.join(tmp, "hero.png"))
        _im("convert", "-size", "%dx%d" % (width, height), "xc:#1a1917", strip, "-geometry", "+0+0", "-composite",
            h, "-geometry", "+0+%d" % strip_h, "-composite", "-quality", "74", out)
        shutil.rmtree(tmp)
    else:
        # invariant: one image KEEPS its ratio, it is not cut to 9:16. A wide photo stretched
        # over an upright card loses both the sky and the foreground, which is why it was taken.
        # The page decides how to fit it, because the build hands it the ratio.
        _im("convert", inputs[0], "-resize", "%dx>" % width, "-quality", "74", out)
    return out


def ledger_free(paths, name):
    """A site without a real og:image returns its logo, the same for every page, and a logo on a
    card lies worse than an empty background. The same fingerprint under another name fails."""
    ledger = media_path("media/.prints")
    h = hashlib.md5(b"".join(open(p, "rb").read() for p in paths)).hexdigest()
    known = {}
    if os.path.exists(ledger):
        for line in open(ledger, encoding="utf-8"):
            k, _, v = line.strip().partition(" ")
            if k:
                known[k] = v
    assert known.get(h, name) == name, "same image as '%s': the site returned its logo instead of a photo" % known[h]
    known[h] = name
    os.makedirs(os.path.dirname(ledger), exist_ok=True)
    open(ledger, "w", encoding="utf-8").write("".join("%s %s\n" % kv for kv in sorted(known.items())))


def fetch(url, name, width=None, collage=False):
    images = find_images(url, 12 if collage else 1)     # some fall out at the filter
    assert images, "no image on the page that looks like content: " + url
    tmp, local, seen = tempfile.mkdtemp(), [], set()
    for i, u in enumerate(images):
        p = os.path.join(tmp, "img%d" % i)
        try:
            download(u, p)
        except Exception:
            continue
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        if is_photo(p) and h not in seen:                # the same image twice in one listing
            seen.add(h)
            local.append(p)
    assert local, "no downloaded image looks like a photograph: " + url
    ledger_free(local[:1], name)
    out = store(local[:4], name, width, collage)
    shutil.rmtree(tmp)
    return "media/" + os.path.basename(out), os.path.getsize(out)


def fetch_video(url, name, seconds=None):
    """Download, cut to the first seconds, scale to 720 wide, drop the sound.

    The card plays muted, because a phone will not start a video with sound by itself, and a
    sound track nobody hears only carries megabytes. Someone else's video is a work: use it for
    a card about that video, not as decoration. SKILL.md has the rule.
    """
    seconds = seconds or CFG["video_seconds"]
    raw = os.path.join(tempfile.mkdtemp(), "raw.mp4")
    subprocess.run(["yt-dlp", "-q", "--no-playlist", "-S", "res:720,ext:mp4:m4a", "-o", raw, url], check=True)
    out = media_path("media/" + name + ".mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-t", str(seconds), "-an",
                    "-vf", "scale='min(720,iw)':-2", "-c:v", "libx264", "-preset", "slow", "-crf", "30",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
    mb = os.path.getsize(out) / 1e6
    if mb > CFG["video_max_mb"]:
        os.remove(out)
        raise AssertionError("the video is %.1f MB and the limit is %.1f: shorten it or take an image" % (mb, CFG["video_max_mb"]))
    return "media/" + os.path.basename(out), os.path.getsize(out)


# --fill: every card of a day gets an image, or the report says which ones did not.

def slug(text, limit=40):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:limit] or "card"


def openverse(query):
    """First CC image for the NAME OF A THING, as (url, credit), or None. Needs no key. A service
    that returns a random photo is exactly the lying image SKILL.md forbids, and so is a search
    for a topic: "garden" finds a meadow for a card about a greenhouse."""
    if not query:
        return None
    url = OPENVERSE + "?" + urllib.parse.urlencode({"q": query, "page_size": 5, "license_type": "all-cc", "mature": "false"})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            hits = json.load(r).get("results") or []
    except Exception:
        return None
    h = next((h for h in hits if h.get("url") and not h["url"].lower().endswith(".svg")), None)
    return h and (h["url"], {"creator": h.get("creator") or "", "license": "%s %s" % (h.get("license") or "", h.get("license_version") or ""),
                             "page": h.get("foreign_landing_url") or h["url"]})


def query_for(card):
    """What to search for: a fact that NAMES the thing, or None. The hook is a sentence about the
    owner, the title of the row is a topic, and an amount or a date names nothing."""
    for pair in card.get("facts") or []:
        if len(pair) == 2 and 3 < len(str(pair[1])) < 40 and not re.search(r"\d", str(pair[1])):
            return str(pair[1])
    return None


def store_direct(url, name):
    """A DIRECT image url, stored as a card cover.

    invariant: fetch() takes a PAGE and scrapes its og:image, so handing it a thumbnail url fails.
    invariant: the card gets `media/<file>`, never the absolute path store() returns. With the
    absolute one a feed shipped where every image was missing while the build check passed,
    because the file did exist on the machine that built it.
    """
    try:
        raw = os.path.join(tempfile.mkdtemp(), "raw")
        download(url, raw)
        if os.path.getsize(raw) < 3000:
            return None            # a tracking pixel or an error page, not a photo
        ledger_free([raw], name)   # the same picture under a second name is a placeholder, not media
        return "media/" + os.path.basename(store([raw], name))
    except Exception:
        return None


def fill(path, dry=False):
    feed = json.load(open(path, encoding="utf-8"))
    assert "rows" in feed, "no `rows` in %s" % path
    # invariant: every searched image is listed with its query, because the agent must LOOK at
    # each one before it stays (SKILL.md, rule 6). A count would hide what was put on the card.
    report = {"had": 0, "from_source": 0, "from_page": [], "from_openverse": [], "without_media": []}
    for row in feed["rows"]:
        cover = row.get("cover") or {}
        for i, card in enumerate([cover] + list(row.get("stories") or [])):
            if card.get("media") or card.get("video"):
                report["had"] += 1
                continue
            got = None
            # `image` is the thumbnail pull-signals.py already took from the feed
            name = "%s-%d" % (slug(row["id"]), i)
            got = None if dry or not card.get("image") else store_direct(card["image"], name)
            if got:
                report["from_source"] += 1
            src = card.get("source")
            page = (src.get("url") if isinstance(src, dict) else None) or next((l.get("href") for l in card.get("links") or []), None)
            if not got and not dry and page:          # the page's own image, before any search
                try:
                    got = fetch(page, name)[0]
                    report["from_page"].append({"card": "%s#%d" % (row["id"], i), "page": page, "file": got})
                except Exception:
                    got = None
            if not got and not dry:
                found = openverse(query_for(card))
                got = found and store_direct(found[0], name)
                if got:
                    report["from_openverse"].append({"card": "%s#%d" % (row["id"], i), "query": query_for(card), "file": got, **found[1]})
            if got:
                card["media"] = got
                card.pop("image", None)
            if not got:
                report["without_media"].append("%s#%d" % (row["id"], i))
    if not dry:
        open(path, "w", encoding="utf-8").write(json.dumps(feed, ensure_ascii=False, indent=1))
    return report


def _check():
    """No network. The ImageMagick half runs only where ImageMagick is."""
    assert slug("Crème & brûlée!") == "creme-brulee" and slug("") == "card"
    assert query_for({"facts": [["Price", "1,240 EUR"], ["Repo", "owner/project"]]}) == "owner/project"
    assert query_for({"facts": [["Why", "because this is far too long to be a term anyone would search for"]]}) is None
    assert openverse(None) is None, "a card that names nothing gets no searched image"
    assert JUNK.search("https://cdn.example.com/assets/images/logos/x.png")
    assert not JUNK.search("https://img.example.com/abc/rs:fit:1920:1080:0/def.jpeg")
    assert IMAGE.findall('src="https://x.example/a/b.jpeg?w=1" x') == ["https://x.example/a/b.jpeg?w=1"]
    assert fill.__defaults__ == (False,)
    if not (shutil.which("magick") or shutil.which("convert")):
        print("ok (no ImageMagick here: store, is_photo and the ledger were not run)")
        return
    global media_path
    real, tmp = media_path, tempfile.mkdtemp()
    media_path = lambda rel: os.path.join(tmp, rel)
    try:
        src = os.path.join(tmp, "src.png")
        _im("convert", "-size", "800x600", "plasma:", src)
        assert is_photo(src)
        logo = os.path.join(tmp, "logo.png")
        _im("convert", "-size", "600x90", "xc:white", logo)
        assert not is_photo(logo), "a wordmark passed as a photo"
        one = store([src], "one", width=200)
        assert image_size(one) == (200, 150), image_size(one)       # the ratio is kept
        many = store([src, src, src], "many", width=180, collage=True)
        assert image_size(many) == (180, 320), image_size(many)
        ledger_free([src], "first")
        ledger_free([src], "first")                                  # the same name again is fine
        try:
            ledger_free([src], "second")
        except AssertionError:
            pass
        else:
            raise AssertionError("a duplicate passed")
    finally:
        media_path = real
        shutil.rmtree(tmp)
    print("ok")


def main():
    known = {"--check", "--fill", "--dry", "--collage", "--width", "--video", "--seconds"}
    flags = [a for a in sys.argv[1:] if a.startswith("-")]
    if set(flags) - known or not sys.argv[1:]:
        print(__doc__)
        return 0 if flags == ["--help"] else 2
    if "--check" in flags:
        return _check()
    opt = lambda f, d: int(sys.argv[sys.argv.index(f) + 1]) if f in flags else d
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("-") and sys.argv[i - 1] not in ("--width", "--seconds")]
    if "--fill" in flags:
        print(json.dumps(fill(args[0], "--dry" in flags), ensure_ascii=False, indent=1))
    elif "--video" in flags:
        print("%s  %d B" % fetch_video(args[0], args[1], opt("--seconds", None)))
    else:
        print("%s  %d B" % fetch(args[0], args[1], opt("--width", None), "--collage" in flags))
    return 0


if __name__ == "__main__":
    sys.exit(main())
