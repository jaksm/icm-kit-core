#!/usr/bin/env python3
"""Build a graph page of a markdown repo: every .md is a node, every path to another .md an edge.

invariant: edges are found with the same patterns as link-check.sh (markdown link, rooted path in
backticks) plus two styles it ignores: a relative path in backticks and a bare file name. A bare
name resolves same folder, then root, then unique name in the repo; an ambiguous one is skipped,
because a wrong edge lies more than a missing one.

The body of every record (without frontmatter) goes into the page for full text search.
invariant: the built page therefore holds the WHOLE repo. It is never committed and never shared.

The page speaks English. _config/graph.json at the repo root overrides any label, and sets
`archive` (prefix of the greyed out groups), `nested` (folders whose children are the groups)
and `out` (where the page is written, default pages/graph.html).

    python3 core/workflows/graph/scripts/build-graph-page.py [--check | --demo]

--demo writes a mock base of about sixty records (areas, skills, an archive, orphans) into a scratch folder, builds its graph
into previews/graph.html and removes the scratch folder. Nothing of an owner's is read.
"""
import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# invariant: this file lives at <repo>/core/workflows/graph/scripts/, so the root is four folders up.
# Not asked of git: inside a commit hook GIT_DIR is set and rev-parse can answer with another checkout.
# ICM_ROOT overrides it: that is how --demo builds the graph of a mock base without touching anyone's ICM.
ROOT = os.environ.get("ICM_ROOT") or os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SKIP = {"_import", "node_modules"}   # plus dot folders at the root
TEMPLATE = os.path.join(HERE, "template/graph-template.html")
# the owner's changed copy of the template wins over the one in core/
_own = os.path.join(ROOT, "_config/overrides/core/workflows/graph/template/graph-template.html")
if os.path.exists(_own):
    TEMPLATE = _own

LABELS = {
    "canvas": "Graph of the records", "search": "Search a record, a path or text",
    "searchLabel": "Search", "settings": "Settings", "legend": "Color legend",
    "colors": "Colors by group", "closeSettings": "Close settings", "filters": "Filters",
    "display": "Display", "forces": "Forces", "all": "all", "noArchive": "no archive",
    "orphans": "orphans", "arrows": "arrows", "nameThreshold": "name threshold",
    "nodeSize": "node size", "lineWidth": "line width", "centering": "centering",
    "repulsion": "repulsion", "linkPull": "link pull", "linkLength": "link length",
    "onlyGroup": "Click shows only this group; click again restores all; Shift or Cmd adds",
    "onlyPre": "Click shows only ", "onlyPost": "; click again restores all; Shift or Cmd adds",
    "noStatus": "no status", "legendRecord": "record", "legendUntyped": "untyped",
    "total": "total", "closePanel": "Close panel", "pointsTo": "Points to",
    "pointedBy": "Pointed to by", "morePre": "", "morePost": " more matches in the text",
    "archive": "archive", "root": "root", "nested": [], "out": "pages/graph.html",
}
_cfg = os.path.join(ROOT, "_config/graph.json")
if os.path.exists(_cfg):
    LABELS.update(json.load(open(_cfg, encoding="utf-8")))
OUT = os.path.join(ROOT, LABELS["out"])

MD_LINK = re.compile(r"\]\(([^)\s]+?\.md)(?:#[^)]*)?\)")
BACKTICK = re.compile(r"`([^`\s<>]+?\.md)`")
TOPS = [d for d in sorted(os.listdir(ROOT)) if os.path.isdir(os.path.join(ROOT, d)) and d not in SKIP and not d.startswith(".")]
# a folder in backticks points at its entry file: a skill at SKILL.md, an area at CONTEXT.md
FOLDER = re.compile(r"`((?:%s)/[^`\s<>.]+?)/?`" % "|".join(map(re.escape, TOPS)))


def files():
    for d, dirs, fs in os.walk(ROOT):
        # dot folders are skipped at the root only (.git, tool folders); an imported archive may keep records in them
        dirs[:] = [x for x in dirs if x not in SKIP and not (d == ROOT and x.startswith("."))]
        for f in fs:
            if f.endswith(".md"):
                yield os.path.relpath(os.path.join(d, f), ROOT)


def frontmatter(text):
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    fm = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def body(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            text = text[end + 4:]
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def group(p):
    parts = p.split("/")
    if len(parts) == 1:
        return LABELS["root"]
    if parts[0] in LABELS["nested"] and len(parts) > 2:
        return parts[1]
    if parts[0] == LABELS["archive"]:
        return parts[0] + "/" + parts[1] if len(parts) > 2 else parts[0]
    return parts[0]


def _lib():
    """Build script of the shared component library: it inlines the stylesheet and module."""
    # installed: <icm>/core/ui; in the kit's own checkout the library is beside core/workflows
    for lib in (os.environ.get("ICM_LIB", ""), os.path.join(ROOT, "core/ui"), os.path.join(HERE, "../../ui")):
        if lib and os.path.exists(os.path.join(lib, "build.py")):
            break
    else:
        sys.exit("component library not found at core/ui; set ICM_LIB to the folder that holds build.py")
    spec = importlib.util.spec_from_file_location("icmlib", os.path.join(lib, "build.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fill_labels(template):
    for k, v in LABELS.items():
        if isinstance(v, str):
            # a label lands inside an HTML attribute or a JS string, so it may not be able to close either
            assert not re.search(r'["<>`\\]', v), "label %s holds a character that would break the page" % k
            template = template.replace("{{%s}}" % k, v)
    left = re.findall(r"\{\{\w+\}\}", template)
    assert not left, "template tokens without a label: %s" % sorted(set(left))
    return template


def main():
    paths = sorted(files())
    known = set(paths)
    by_name = defaultdict(list)
    for p in paths:
        by_name[os.path.basename(p)].append(p)

    def resolve(src, target):
        target = target.split("#")[0]
        if target.startswith("/"):
            return None
        folder = os.path.dirname(src)
        if "/" not in target:
            for cand in (os.path.join(folder, target), target):
                if cand in known:
                    return cand
            same = by_name.get(target, [])
            return same[0] if len(same) == 1 else None
        if target in known:
            return target
        rel = os.path.normpath(os.path.join(folder, target))
        return rel if rel in known else None

    nodes, edges = [], set()
    for p in paths:
        text = open(os.path.join(ROOT, p), encoding="utf-8", errors="replace").read()
        fm = frontmatter(text)
        name = os.path.basename(p)
        kind = fm.get("type", "").capitalize() or ("Context" if name == "CONTEXT.md" or (p == name and name[:-3].isupper() and name != "README.md") else "Untyped")
        title = fm.get("title")
        if not title:
            m = re.search(r"^# (.+)$", text, re.M)
            title = m.group(1).strip() if m else name[:-3]
        tags = fm.get("tags", "").strip("[]")
        nodes.append({"id": p, "t": title, "d": fm.get("description", "")[:240], "ty": kind,
                      "g": group(p), "st": fm.get("status", ""), "tr": fm.get("trust_tier", ""),
                      "tg": [x.strip() for x in tags.split(",") if x.strip()],
                      "b": body(text)})
        targets = MD_LINK.findall(text) + BACKTICK.findall(text)
        for f in FOLDER.findall(text):
            targets += [f + "/SKILL.md", f + "/CONTEXT.md", f + "/README.md"]
        for target in targets:
            r = resolve(p, target)
            if r and r != p:
                edges.add((p, r))

    degree = Counter()
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
    for n in nodes:
        n["k"] = degree[n["id"]]
    data = {"n": nodes, "e": sorted(edges)}
    # invariant: "</" is escaped, or a "</script>" inside some record would close the page's script.
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    if "--check" in sys.argv:
        print("nodes %d, edges %d, orphans %d, JSON %d KB" % (
            len(nodes), len(edges), sum(1 for n in nodes if not n["k"]), len(js) // 1024))
        print("types:", dict(Counter(n["ty"] for n in nodes).most_common()))
        print("groups:", dict(Counter(n["g"] for n in nodes).most_common()))
        assert len(js) < 12_000_000, "JSON too large for a 16 MB page"

    template = open(TEMPLATE, encoding="utf-8").read()
    assert "__DATA__" in template, "the template has no data slot"
    template = _lib().inline(fill_labels(template))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(template.replace("__DATA__", js))
    print("wrote %s, %d KB" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) // 1024))


def demo():
    import random, shutil, subprocess
    kit = os.path.abspath(os.path.join(HERE, "../../.."))
    out = os.path.join(kit if os.path.exists(os.path.join(kit, "install.sh")) else os.path.join(ROOT, "pages"), "previews")
    root = os.path.join(out, ".graph-root")
    shutil.rmtree(root, ignore_errors=True)
    rnd = random.Random(11)
    areas = {"travel": ["lisbon", "kyoto-2027", "packing-list", "rail-passes", "visa-notes", "travel-budget"],
             "health": ["knee-rehab", "physio-visits", "sleep-log", "blood-tests", "running-plan"],
             "money": ["budget", "tax-deadlines", "insurance", "savings-goal", "subscriptions", "receipts-2026"],
             "home": ["bathroom", "tiles", "plumber", "garden-beds", "tool-list"],
             "learning": ["bread", "starter-notes", "spanish", "reading-list", "course-notes"],
             "people": ["family", "friends", "gift-ideas", "birthdays"]}
    types, statuses = ["Reference", "Output", "Decision", "Tracking", "Research"], ["active", "active", "active", "draft", "paused"]
    files = {}
    for a, names in areas.items():
        files["domains/%s/CONTEXT.md" % a] = "# %s\n\n%s\n" % (a.capitalize(), "\n".join("- `domains/%s/%s.md`" % (a, n) for n in names))
        for n in names:
            others = rnd.sample(names, min(2, len(names)))
            far = rnd.choice(list(areas))
            body = " ".join("See [%s](%s.md)." % (o, o) for o in others if o != n) + " Also `domains/%s/%s.md`." % (far, rnd.choice(areas[far]))
            files["domains/%s/%s.md" % (a, n)] = ("---\ntype: %s\ntitle: %s\ndescription: A mock record about %s.\nstatus: %s\ntrust_tier: verified\ntags: [%s]\n---\n\n# %s\n\n%s\n"
                                                  % (rnd.choice(types), n.replace("-", " ").capitalize(), n.replace("-", " "), rnd.choice(statuses), a, n.replace("-", " ").capitalize(), body))
    for sk in ["morning-review", "trip-planner", "monthly-close"]:
        files["skills/%s/SKILL.md" % sk] = "---\ntype: Skill\ntitle: %s\nstatus: active\n---\n\n# %s\n\nReads `domains/money/budget.md` and `domains/travel/lisbon.md`.\n" % (sk, sk)
    for old in ["old-flat", "2019-trip", "former-job"]:
        files["archive/%s.md" % old] = "---\ntype: Reference\ntitle: %s\nstatus: archived\n---\n\n# %s\n\nKept for the record.\n" % (old, old)
    for lone in ["loose-idea", "unfiled-note"]:
        files["%s.md" % lone] = "# %s\n\nNothing points here yet.\n" % lone
    files["_config/graph.json"] = '{"nested": ["domains"]}\n'   # one group, and so one color, per area
    files["ROUTER.md"] = "# Router\n\n%s\n" % "\n".join("- `domains/%s/CONTEXT.md`" % a for a in areas)
    for rel, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(root, rel)) or root, exist_ok=True)
        open(os.path.join(root, rel), "w", encoding="utf-8").write(text)
    lib = next(p for p in (os.environ.get("ICM_LIB", ""), os.path.join(ROOT, "core/ui"), os.path.join(HERE, "../../ui")) if p and os.path.exists(os.path.join(p, "build.py")))
    r = subprocess.run([sys.executable, os.path.abspath(__file__)], env={**os.environ, "ICM_ROOT": root, "ICM_LIB": lib})
    if r.returncode == 0:
        shutil.copy(os.path.join(root, "pages/graph.html"), os.path.join(out, "graph.html"))
        print("wrote %s, %d mock records" % (os.path.join(out, "graph.html"), len(files)))
    shutil.rmtree(root, ignore_errors=True)
    return r.returncode


if __name__ == "__main__":
    # invariant: an unknown flag stops the run. This script writes files, and a flag that is silently
    # ignored (`--help` did this) writes them for someone who only asked a question.
    unknown = [a for a in sys.argv[1:] if a.startswith("-") and a not in ("--check", "--demo")]
    if unknown:
        print(__doc__ if unknown == ["--help"] else "unknown flag: %s; known: --check, --demo" % " ".join(unknown))
        sys.exit(0 if unknown == ["--help"] else 2)
    sys.exit(demo()) if "--demo" in sys.argv else main()
