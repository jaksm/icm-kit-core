#!/usr/bin/env python3
"""Bundle the ICM component library and inline it into an artifact template.

The library is many small files (one component, one .js and one .css) so it reads like any
component library. The page, however, must be ONE self-contained file: the artifact CSP
blocks external scripts we do not control, and offline tolerance needs zero runtime fetches.
This script is the bridge.

    python3 build.py --bundle   # rebuild dist/icm.js
    python3 build.py --check

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
# Palettes come last among the tokens: each is scoped to [data-palette], so it only overrides on a page that asks.
TOKENS = ["colors.css", "typography.css", "motion.css", "layout.css", "surface.css", "palettes/archive.css"]


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
    return template.replace("/*ICM-CSS*/", stylesheet()).replace("/*ICM-JS*/", js)


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


def _check():
    css = stylesheet()
    assert "--c-fg" in css and ".on-photo" in css, "surface tokens are missing"
    js = module()
    assert "customElements.define" in js and len(js) > 20000, len(js)
    assert "import" not in js.split("\n")[0], "the bundle is not self-contained"
    check_schema()
    s = inline("<style>/*ICM-CSS*/</style><script type=module>/*ICM-JS*/</script>")
    assert "</script>" not in s.split("<script type=module>")[1][:-9], "the module closes its own script tag"
    print("ok")


if __name__ == "__main__":
    if "--check" in sys.argv:
        _check()
    elif "--bundle" in sys.argv:
        print("wrote " + bundle())
    elif "--workbench" in sys.argv:
        # every token and component on one page, under every palette and theme; not committed
        out = os.path.join(LIB, "workbench/index.html")
        open(out, "w", encoding="utf-8").write(inline(open(os.path.join(LIB, "workbench/index.src.html"), encoding="utf-8").read()))
        print("wrote workbench/index.html, %d B; serve the folder and open it" % os.path.getsize(out))
    else:
        print("%d B of style, %d B of module" % (len(stylesheet()), len(module())))
