#!/usr/bin/env python3
"""Write the mock feed's images: soft two-color gradients as PNG, from the standard library only, so the kit ships no binary
and asks for no image tool. Usage: make-demo-media.py <folder>. Upright 540x810, one wide 960x540 (the feed frames wide media)."""
import os
import struct
import sys
import zlib

IMAGES = {"travel.png": ((54, 96, 140), (226, 170, 110), 540, 810), "car.png": ((30, 48, 70), (150, 170, 190), 540, 810),
          "health.png": ((60, 110, 84), (190, 214, 170), 540, 810), "money.png": ((70, 60, 110), (214, 180, 120), 540, 810),
          "learning.png": ((120, 70, 50), (236, 200, 150), 540, 810), "bread.png": ((150, 96, 40), (240, 214, 170), 540, 810),
          "coast-wide.png": ((40, 90, 130), (230, 200, 160), 960, 540)}


def png(path, a, b, w, h):
    rows = bytearray()
    for y in range(h):
        rows.append(0)
        for x in range(w):
            t = (y / h) * .75 + (x / w) * .25
            k = t * t * (3 - 2 * t)                       # smoothstep, so the image has a sky and a ground instead of a ramp
            rows += bytes(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
    chunk = lambda tag, data: struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(bytes(rows), 6)) + chunk(b"IEND", b""))


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, (a, b, w, h) in IMAGES.items():
        png(os.path.join(out, name), a, b, w, h)
    print("wrote %d images to %s" % (len(IMAGES), out))
