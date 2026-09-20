"""Shared by the feed scripts: where the ICM root, the config and the data folder are."""
import json
import os

# invariant: installed at <icm>/core/workflows/feed/scripts/, so the ICM root is four folders up
# from this folder. Git is not asked: inside a commit hook in a worktree it answers wrongly.
# ICM_ROOT overrides it: that is how `build-feed-page.py --demo` builds the mock base in template/demo/ without touching anyone's ICM.
ROOT = os.environ.get("ICM_ROOT") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))

# invariant: every number here is an agreement, not science, and the ones about hosts are dated
# measurements that rot. They live in _config/feed.json so the owner's agent can retune them
# without touching core; recipes/any-reader.md says how each was measured.
DEFAULTS = {
    "data": "domains/system/data/feed",      # <data>/<date>.json, <data>/signals/<date>/, <data>/diary.csv
    "media_dir": "pages/media",              # image and video files; a card names one as media/<file>
    "out": "pages/feed.html",
    "actions": "_config/actions.json",
    "max_age_hours": 48,
    "reddit_gap": 60, "reddit_budget": 45,   # measured 2026-09-19: one anonymous request per ~60 s
    "youtube_gap": 8.0, "youtube_budget": 25, "breaker_at": 3,   # measured 2026-09-19: the block is per IP per day
    "max_chars": 12000,
    "video_seconds": 6, "video_max_mb": 3.0, "image_width": 1080,
    "junk_paths": [],                        # extra path words that mark a logo or a banner on the owner's sites
    "covers": {},                            # {"row id": "media/<file>"}: the standing cover of a row
    "hosts": {},                             # {"regex of a host": "button label"}; without a match: "Open on <host>"
    "seen_ms": 1200,
    "labels": {},
}


def config():
    c = dict(DEFAULTS)
    p = os.path.join(ROOT, "_config/feed.json")
    if os.path.exists(p):
        c.update(json.load(open(p, encoding="utf-8")))
    return c


def data(*parts):
    return os.path.join(ROOT, config()["data"], *parts)


def media_path(rel):
    """Where the file behind a card's `media/<file>` is on disk."""
    return os.path.join(ROOT, config()["media_dir"], rel.split("/", 1)[1] if rel.startswith("media/") else rel)


def image_size(path):
    """(width, height) from the header of a WebP, PNG or JPEG file, or None. No external tool.

    invariant: a cloud runner may have no ImageMagick at all, and where it has one it is often
    version 6, which has `identify` and no `magick`. A build that needs either dies on a machine
    that looks identical to the one where it worked, so sizes are read here first.
    """
    with open(path, "rb") as f:
        head = f.read(32)
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            tag = head[12:16]
            if tag == b"VP8X":
                return int.from_bytes(head[24:27], "little") + 1, int.from_bytes(head[27:30], "little") + 1
            if tag == b"VP8L":
                b = int.from_bytes(head[21:25], "little")
                return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
            if tag == b"VP8 ":
                return int.from_bytes(head[26:28], "little") & 0x3FFF, int.from_bytes(head[28:30], "little") & 0x3FFF
            return None
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
        if head[:2] == b"\xff\xd8":
            f.seek(2)
            while True:
                marker = f.read(2)
                if len(marker) < 2 or marker[0] != 0xFF:
                    return None
                size = int.from_bytes(f.read(2), "big")
                # SOF0..SOF15, except DHT (C4), JPG (C8) and DAC (CC)
                if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                    f.read(1)
                    h = int.from_bytes(f.read(2), "big")
                    return int.from_bytes(f.read(2), "big"), h
                f.seek(size - 2, 1)
    return None


def video_size(path):
    """(width, height) from the largest `tkhd` box of an MP4 or MOV file, or None. No ffprobe."""
    best = None
    blob = open(path, "rb").read()
    i = 0
    while True:
        i = blob.find(b"tkhd", i)
        if i < 0:
            return best
        i += 4
        version = blob[i] if i < len(blob) else 0
        # `tkhd` is searched through the whole file, so a false hit inside the data is refused by
        # the size of the box: 92 bytes for version 0 and 104 for version 1, header included.
        if int.from_bytes(blob[i - 8:i - 4], "big") != (104 if version == 1 else 92):
            continue
        # body: version and flags (4), times, id and duration (20 or 32), reserved (8), layer,
        # group, volume and reserved (8), matrix (36), then width and height as 16.16
        at = i + 4 + (32 if version == 1 else 20) + 8 + 8 + 36
        if at + 8 <= len(blob):
            w, h = int.from_bytes(blob[at:at + 2], "big"), int.from_bytes(blob[at + 4:at + 6], "big")
            if w and h and (not best or w * h > best[0] * best[1]):   # the audio track has one with zeros
                best = (w, h)
