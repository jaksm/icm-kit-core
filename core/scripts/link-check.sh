#!/bin/bash
# Find pointers in markdown to files that do not exist. Run before a commit that moved or deleted files.
# LINK_CHECK_SKIP: space separated path prefixes to ignore (default: .git).
cd "$(git rev-parse --show-toplevel)" || exit 1
python3 - <<'PY'
import re, glob, os, sys
skip = tuple(os.environ.get('LINK_CHECK_SKIP', '.git').split())
# a backticked path counts as a pointer only when its first segment is a real top-level folder
tops = '|'.join(re.escape(d) for d in sorted(os.listdir('.')) if os.path.isdir(d) and not d.startswith('.'))
ROOTED = re.compile(r'`((?:%s)/[^`<>*{}$ ]+\.(?:md|csv|sh|py))`' % tops) if tops else None
bad, n = [], 0
for p in glob.glob('**/*.md', recursive=True):
    if p.startswith(skip):
        continue
    n += 1
    d = os.path.dirname(p)
    text = open(p, encoding='utf-8').read()
    for t in re.findall(r'\]\(([^)]+\.md)\)', text):
        if t.startswith(('http://', 'https://')):
            continue
        if not os.path.exists(t) and not os.path.exists(os.path.normpath(os.path.join(d, t))):
            bad.append((p, t))
    for t in (ROOTED.findall(text) if ROOTED else []):
        # a skill names its own scripts/x.py relative to itself, which collides with a top-level scripts/
        if not os.path.exists(t) and not os.path.exists(os.path.join(d, t)):
            bad.append((p, t))
    # invariant: absolute paths are checked like repo paths. Without this, 446 pointers into a
    # home directory that no longer existed passed silently for months.
    for t in re.findall(r'((?:/Users|/home)/[^\s`)\]<>"\']+)', text):
        t = t.rstrip('.,;:')
        if not os.path.exists(t):
            bad.append((p, t))

for p, t in bad:
    print('link-check: %s points to %s, which does not exist' % (p, t))
print('link-check: %d dangling links in %d files' % (len(bad), n))
sys.exit(1 if bad else 0)
PY
