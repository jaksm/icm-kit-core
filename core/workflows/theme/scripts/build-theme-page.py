#!/usr/bin/env python3
"""Builds the Theme editor page: <icm-theme-editor> beside one of everything in icm-ui, so a theme is judged on the whole system.

    python3 build-theme-page.py            # writes <icm>/pages/theme.html, with the owner's own themes from _config/themes/
    python3 build-theme-page.py --demo     # previews/theme.html in the kit's checkout, no _config needed
    python3 build-theme-page.py --check    # the template has its slots and every label, and the page builds

The page never writes to the repo. Save puts the choice in the artifact's db (theme/current) and "Copy for the agent" puts it on
the clipboard; core/skills/theme/SKILL.md says how the agent turns either into _config/theme.json.
"""
import glob
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("ICM_ROOT") or os.path.abspath(os.path.join(HERE, "../../../.."))
TEMPLATE = os.path.join(HERE, "../template/theme-template.html")
LABELS = {"theme": "Theme", "system": "icm-ui", "title": "Everything, in your theme", "lede": "Pick a theme, a palette and a type set, or make a palette from a color. Every part of the system is on this page, so what you see is what every page you build will look like.",
          "color": "Color", "type": "Type", "controls": "Controls", "surfaces": "Surfaces, rows, meters", "components": "Components"}


def _lib():
    found = [p for p in (os.environ.get("ICM_LIB") or "", os.path.join(ROOT, "core/ui"), os.path.join(HERE, "../../../ui"))
             if p and os.path.exists(os.path.join(p, "build.py"))]
    assert found, "the UI library was not found; set ICM_LIB"
    spec = importlib.util.spec_from_file_location("icmlib", os.path.join(found[0], "build.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def page():
    lib, src = _lib(), open(TEMPLATE, encoding="utf-8").read()
    own = os.path.join(ROOT, "_config/labels.json")
    labels = {**LABELS, **(json.load(open(own, encoding="utf-8")).get("theme", {}) if os.path.exists(own) else {})}
    missing = [k for k in re.findall(r"\{\{(\w+)\}\}", src) if k not in labels]
    assert not missing, "labels without a text: %s" % missing
    assert "/*ICM-EDITOR*/" in src, "the template has no slot /*ICM-EDITOR*/"
    src = re.sub(r"\{\{(\w+)\}\}", lambda m: labels[m[1]], src)
    hosts = sorted(glob.glob(os.path.join(ROOT, "core/adapters/*/page-host.js")) + glob.glob(os.path.join(HERE, "../../../adapters/*/page-host.js")))
    src = src.replace("/*ICM-HOST*/", open(hosts[0], encoding="utf-8").read() if hosts else "")   # the adapter's page side, as in the feed
    return lib.inline(src.replace("/*ICM-EDITOR*/", lib.themes_data() + lib.editor_module()))


def _write(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(page())
    print(path)


def _check():
    html = page()
    assert "icm-theme-editor" in html and "ICM_THEMES" in html and "{{" not in html
    assert html.count("customElements.define") >= 2, "the library or the editor is missing from the page"
    print("ok")


if __name__ == "__main__":
    unknown = [a for a in sys.argv[1:] if a.startswith("-") and a not in ("--check", "--demo")]
    if unknown:
        sys.exit("unknown flag: " + " ".join(unknown))
    if "--check" in sys.argv:
        _check()
    elif "--demo" in sys.argv:
        kit = os.path.abspath(os.path.join(HERE, "../../../.."))
        _write(os.path.join(kit, "previews/theme.html"))
    else:
        _write(os.path.join(ROOT, "pages/theme.html"))
