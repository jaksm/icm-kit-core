#!/usr/bin/env python3
"""Bundle the ICM component library and inline it into an artifact template.

The library is many small files (one component, one .js and one .css) so it reads like any
component library. The page, however, must be ONE self-contained file: the artifact CSP
blocks external scripts we do not control, and offline tolerance needs zero runtime fetches.
This script is the bridge.

    python3 build.py --bundle   # rebuild dist/icm.js
    python3 build.py --check    # schema against code, and WCAG AA contrast of the tokens
    python3 build.py --docs     # docs/index.html: the design concept and the documentation, from the real components

Used from an artifact's own build script:

    from build import inline
    page = inline(template)        # fills /*ICM-CSS*/ and /*ICM-JS*/

The library speaks English. A labels.json is injected as globalThis.ICM_LABELS, so a repo gets
its own language without touching a component. It is looked for in $ICM_LABELS, then in
_config/labels.json at the root of the repo that runs the build, then beside this folder. Never
inside it: this folder is replaced whole on update.
"""
import glob
import json
import os
import re
import subprocess
import sys

LIB = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(LIB, "dist/icm.js")
VENDOR = os.path.join(LIB, "vendor/lit.js")


def _labels_path():
    # invariant: vendored as <repo>/core/ui, the repo root is two folders up. Not asked of git: inside a
    # commit hook GIT_DIR is set and rev-parse can answer with another checkout (seen in a worktree).
    core = os.path.dirname(LIB)
    root = os.path.dirname(core) if os.path.basename(core) == "core" else subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    for p in (os.environ.get("ICM_LABELS", ""), os.path.join(root, "_config/labels.json") if root else "",
              os.path.join(os.path.dirname(LIB), "labels.json")):
        if p and os.path.exists(p):
            return p
    return ""

# invariant: tokens load in this order and nothing else may come before them. Every component
# reads --c-* from a surface class, and the surface classes are defined in surface.css.
# invariant: one design system. There are no palettes: a page that wants its own look overrides tokens itself.
TOKENS = ["colors.css", "typography.css", "motion.css", "layout.css", "data.css", "surface.css"]

# The fonts the default palette names. A page puts this in its <head>; the library never fetches anything itself.
FONTS_LINK = '<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">'


def stylesheet():
    """Every .css in the library, tokens first, as one string."""
    parts = []
    for name in TOKENS:
        put = os.path.join(LIB, "tokens", name)
        assert os.path.exists(put), "missing token file: " + name
        parts.append(open(put, encoding="utf-8").read())
    for folder in ("primitives", "components"):
        for put in sorted(glob.glob(os.path.join(LIB, folder, "*.css"))):
            parts.append(open(put, encoding="utf-8").read())
    return "\n".join(parts)


def bundle():
    """Pack index.js into one import-free ESM file. Needs esbuild, once, not at page build."""
    assert os.path.exists(VENDOR), (
        "missing vendor/lit.js; see vendor/README.md")
    os.makedirs(os.path.dirname(DIST), exist_ok=True)
    try:
        subprocess.run(["npx", "--yes", "esbuild", os.path.join(LIB, "index.js"),
                        "--bundle", "--format=esm", "--minify", "--outfile=" + DIST],
                       check=True, capture_output=True)
    except FileNotFoundError:
        sys.exit("esbuild is not available. Run:\n  npx --yes esbuild index.js --bundle "
                 "--format=esm --minify --outfile=dist/icm.js")
    except subprocess.CalledProcessError as e:
        sys.exit("esbuild failed:\n" + e.stderr.decode("utf-8", "replace"))
    return DIST


def module():
    """The bundled library, rebuilt when a source file is newer than dist."""
    src = ([os.path.join(LIB, "index.js"), VENDOR]
           + glob.glob(os.path.join(LIB, "*/*.js")))
    if not os.path.exists(DIST) or max(os.path.getmtime(p) for p in src) > os.path.getmtime(DIST):
        bundle()
    return open(DIST, encoding="utf-8").read()


def inline(template):
    """Fill /*ICM-CSS*/ and /*ICM-JS*/ in a template. Fails loudly on a missing slot, because
    a page that silently keeps its own copy of the library is exactly what this removes."""
    for slot in ("/*ICM-CSS*/", "/*ICM-JS*/"):
        assert slot in template, "the template has no slot " + slot
    # </ inside the module would close <script> early
    js = module().replace("</", "<\\/")
    LABELS = _labels_path()
    if LABELS:
        # invariant: the assignment sits in the same script, ahead of the bundle, so LABELS reads it
        labels = json.dumps(json.load(open(LABELS, encoding="utf-8")), ensure_ascii=False)
        js = "globalThis.ICM_LABELS=%s;\n" % labels.replace("</", "<\\/") + js
    # a page that wants the fonts the tokens name puts <!--ICM-FONTS--> in its head; the library itself never fetches anything
    return template.replace("<!--ICM-FONTS-->", FONTS_LINK).replace("/*ICM-CSS*/", stylesheet()).replace("/*ICM-JS*/", js)


def schema():
    return json.load(open(os.path.join(LIB, "schema.json"), encoding="utf-8"))


def check_schema():
    """Schema and code must not drift: every component in schema.json has a file that defines
    its custom element, and every defined element has a row in the schema."""
    s = schema()
    in_code = set()
    for folder in ("primitives", "components"):
        for put in glob.glob(os.path.join(LIB, folder, "*.js")):
            for m in re.finditer(r"customElements\.define\('([a-z-]+)'",
                                 open(put, encoding="utf-8").read()):
                in_code.add(m.group(1))
    # `element: null` marks a component that is plain text on the card, not an element
    in_schema = {v["element"] for v in s["components"].values() if v.get("element")}
    in_code -= {"icm-icon", "icm-button"}   # primitives used BY components, not by content
    assert not (in_schema - in_code), "in the schema, not in code: %s" % (in_schema - in_code)
    assert not (in_code - in_schema), "in code, not in the schema: %s" % (in_code - in_schema)
    return True


def _hexes(block):
    return {k: v for k, v in re.findall(r"(--[a-z0-9-]+):\s*(#[0-9a-fA-F]{3,6})\b", block)}


def _lum(h):
    h = h.lstrip("#"); h = "".join(c * 2 for c in h) if len(h) == 3 else h
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    r, g, bl = (f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    return .2126 * r + .7152 * g + .0722 * bl


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def check_contrast():
    """WCAG AA as a script, not a sentence: every text token on every ground it is used on, in each theme.
    4.5:1 for text; 3:1 for the things that are only shapes (borders of controls, the accent as a fill)."""
    read = lambda n: open(os.path.join(LIB, "tokens", n), encoding="utf-8").read()
    colors, data = read("colors.css"), read("data.css")
    block = lambda css, sel: css[css.index(sel):].split("}", 1)[0]
    base = {**_hexes(block(colors, ":root{")), **_hexes(block(data, ":root{"))}
    themes = {
        "light": base,
        "dark": {**base, **_hexes(block(colors, ':root[data-theme="dark"]')), **_hexes(block(data, ':root[data-theme="dark"]'))},
    }
    photo = {**_hexes(block(data, ".on-photo{"))}
    bad = []
    for name, t in themes.items():
        pairs = [(fg, bg, 4.5) for fg in ("--ink", "--ink-2", "--ink-muted", "--accent", "--state-good", "--state-warn", "--state-bad") for bg in ("--paper", "--card")]
        pairs += [("--on-accent", "--accent-fill", 4.5), ("--on-mark", "--mark", 4.5), ("--ink", "--paper", 7)]
        # shapes, not text: the fill of a button or a bar, and the first eight category colors, need 3:1 against their ground
        pairs += [(fg, bg, 3) for fg in ["--accent-fill"] + ["--cat-%d" % i for i in range(1, 9)] for bg in ("--paper", "--card")]
        for fg, bg, need in pairs:
            r = contrast(t[fg], t[bg])
            if r < need:
                bad.append("%s: %s %s on %s %s = %.2f, needs %s" % (name, fg, t[fg], bg, t[bg], r, need))
    floor = base["--scrim-floor"]   # text over a photo sits on the scrim; its darkest stop is the ground that is guaranteed
    for fg, v in {**{k: base[k] for k in ("--over", "--over-2", "--over-muted", "--over-accent")}, **photo}.items():
        if contrast(v, floor) < 4.5:
            bad.append("on-photo: %s %s on the scrim floor = %.2f" % (fg, v, contrast(v, floor)))
    assert not bad, "contrast below WCAG AA:\n  " + "\n  ".join(bad)
    return True


def _check():
    css = stylesheet()
    assert "--c-fg" in css and ".on-photo" in css, "surface tokens are missing"
    js = module()
    assert "customElements.define" in js and len(js) > 20000, len(js)
    assert "import" not in js.split("\n")[0], "the bundle is not self-contained"
    check_schema()
    check_contrast()
    s = inline("<style>/*ICM-CSS*/</style><script type=module>/*ICM-JS*/</script>")
    assert "</script>" not in s.split("<script type=module>")[1][:-9], "the module closes its own script tag"
    print("ok")


if __name__ == "__main__":
    if "--check" in sys.argv:
        _check()
    elif "--bundle" in sys.argv:
        print("wrote " + bundle())
    elif "--docs" in sys.argv:
        # the design concept and the documentation in one page, built from the real components; not committed.
        # invariant: the tables come from schema.json and actions.json, so the docs cannot name what does not exist.
        check_schema()
        icons = re.findall(r"^  ([a-zA-Z]+): svg`", open(os.path.join(LIB, "icons/ui.js"), encoding="utf-8").read(), re.M)
        data = json.dumps({"schema": schema(), "actions": json.load(open(os.path.join(LIB, "actions.json"), encoding="utf-8")),
                           "icons": icons, "version": open(os.path.join(LIB, "VERSION")).read().strip()}, ensure_ascii=False).replace("</", "<\\/")
        src = open(os.path.join(LIB, "docs/index.src.html"), encoding="utf-8").read()
        assert "/*ICM-DOCS*/" in src and "<!--ICM-FONTS-->" in src
        out = os.path.join(LIB, "docs/index.html")
        open(out, "w", encoding="utf-8").write(inline(src.replace("/*ICM-DOCS*/", "const DOCS=" + data)))
        print("wrote " + out)
    else:
        print("%d B of style, %d B of module" % (len(stylesheet()), len(module())))
