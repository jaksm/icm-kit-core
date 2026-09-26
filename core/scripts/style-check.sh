#!/bin/bash
# Style rules a machine can check, so they are not left as a sentence someone forgets. Run before a commit.
# STYLE_CHECK_SKIP: space separated path prefixes whose text is not ours to fix (vendored, archived).
# STYLE_TEMPLATES: git pathspec of page templates to check (default: *-template.html).
# STYLE_NO_CYRILLIC=1: flag a Cyrillic letter inside Latin text.
# STYLE_MAX_LINES="200 80": a record and a CONTEXT.md under domains/ and skills/ may not be longer.
#   _config/style-long-files.csv (path,lines) is a ratchet: a listed file may stay that long, not grow.
cd "$(git rev-parse --show-toplevel)" || exit 1
python3 - <<'PY'
import re, subprocess, sys, os

bad = []
skip = tuple(os.environ.get('STYLE_CHECK_SKIP', '').split())
templates = os.environ.get('STYLE_TEMPLATES', '*-template.html')

# invariant: -z and split on NUL, never .split(). Otherwise `git ls-files` quotes names with
# diacritics and spaces, and open() fails on the literal quote character.
def ls(*args):
    out = subprocess.run(['git', 'ls-files', '-z', *args], capture_output=True, text=True).stdout
    return [f for f in out.split('\0') if f and not (skip and f.startswith(skip))]

docs = ls('*.md')

for p in docs:
    for i, line in enumerate(open(p, encoding='utf-8'), 1):
        if chr(0x2014) in line:
            bad.append('%s:%d em dash' % (p, i))
        # an outdated fact is deleted, not struck through; why it went is in the commit
        if re.search(r'~~[^~]+~~', line):
            bad.append('%s:%d struck through text instead of a deletion' % (p, i))

for p in ls():
    name = os.path.basename(p)
    # README.md, SKILL.md, LICENSE and the like are conventional names
    if re.fullmatch(r'[A-Z]+(\.[a-z]+)?', name):
        continue
    if not re.fullmatch(r'[a-z0-9._-]+', name):
        bad.append('%s file name is not lowercase ascii with dashes' % p)

# A page without a viewport meta renders on a phone as an 800px page; without a charset any
# non ASCII text comes out as mojibake. Both are invisible on desktop, so the rule is a script.
for p in (ls(templates) if templates else []):
    t = open(p, encoding='utf-8').read()
    if 'name="viewport"' not in t[:600]:
        bad.append('%s has no <meta name="viewport">' % p)
    if 'charset' not in t[:600]:
        bad.append('%s has no <meta charset="utf-8">' % p)

# A Cyrillic letter inside Latin text passes the eye and the spellchecker and cannot be found by
# grep. For repos written in a Latin script language that also has a Cyrillic one. A line that
# talks about Cyrillic may show it.
if os.environ.get('STYLE_NO_CYRILLIC'):
    for p in docs:
        for i, line in enumerate(open(p, encoding='utf-8'), 1):
            if re.search('[%s-%s]' % (chr(0x400), chr(0x4ff)), line) and 'yrill' not in line and 'iril' not in line:
                bad.append('%s:%d Cyrillic letter in Latin text' % (p, i))
                break

# A length limit that is only a sentence gets crossed and nobody notices. The ratchet lets files that
# were long when the rule arrived stay so until someone shortens them; delete the row then.
if os.environ.get('STYLE_MAX_LINES'):
    record, router = (int(x) for x in os.environ['STYLE_MAX_LINES'].split())
    ratchet = {}
    if os.path.exists('_config/style-long-files.csv'):
        for line in open('_config/style-long-files.csv', encoding='utf-8').read().splitlines()[1:]:
            if line.strip():
                ratchet[line.rsplit(',', 1)[0]] = int(line.rsplit(',', 1)[1])
    for p in docs:
        if not p.startswith(('domains/', 'skills/')) or '/references/' in p and p.startswith('skills/'):
            continue
        n = sum(1 for _ in open(p, encoding='utf-8'))
        limit = ratchet.get(p, router if p.endswith('CONTEXT.md') else record)
        if n > limit:
            bad.append('%s has %d lines, limit %d' % (p, n, limit))

for r in bad:
    print('style-check: ' + r)
print('style-check: %d findings in %d files' % (len(bad), len(docs)))
sys.exit(1 if bad else 0)
PY
