#!/usr/bin/env python3

# One-time converter of the translations of Pingus, from gettext `.po`
# files to Atmos data, which the game reads with `X.load`.
#
#   tools/po.py <data/po of fsantanna/pingus@036852a> <data/po of the port>
#
# Each `LANG.po` becomes `LANG.po.atm`:
#
#   :pingus.po [
#       lang = "de",
#       texts = [ @"Story" = "Geschichte", ... ],
#   ]
#
# Fuzzy and untranslated entries are left out. Writes `index.atm`, the
# languages with the number of texts of each one.

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert import atm_str

def unquote (s):
    s = s.strip()
    assert s[0] == '"' and s[-1] == '"', s
    out, i = [], 1
    while i < len(s) - 1:
        c = s[i]
        if c == '\\':
            i += 1
            out.append({'n':'\n', 't':'\t', '"':'"', '\\':'\\'}.get(s[i], s[i]))
        else:
            out.append(c)
        i += 1
    return ''.join(out)

def parse (path):
    entries = []
    cur = None
    fuzzy = False
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('#,') and 'fuzzy' in line:
            fuzzy = True
        elif line.startswith('msgid '):
            cur = {'id': unquote(line[6:]), 'str': '', 'fuzzy': fuzzy, 'k': 'id'}
            entries.append(cur)
            fuzzy = False
        elif line.startswith('msgstr '):
            cur['str'] = unquote(line[7:])
            cur['k'] = 'str'
        elif line.startswith('"') and cur:
            cur[cur['k']] += unquote(line)
        elif line.strip() == '':
            cur = None
    return [ (e['id'], e['str']) for e in entries
             if e['id'] and e['str'] and not e['fuzzy'] ]

def main (src, dst):
    os.makedirs(dst, exist_ok=True)
    index = []
    for f in sorted(os.listdir(src)):
        if not f.endswith('.po'):
            continue
        lang = f[:-3]
        texts = parse(os.path.join(src, f))
        with open(os.path.join(dst, lang + '.po.atm'), 'w', encoding='utf-8') as out:
            out.write(':pingus.po [\n    lang = %s,\n    texts = [\n' % atm_str(lang))
            for k, v in texts:
                out.write('        @%s = %s,\n' % (atm_str(k), atm_str(v)))
            out.write('    ],\n]\n')
        index.append((lang, len(texts)))
    with open(os.path.join(dst, 'index.atm'), 'w', encoding='utf-8') as out:
        out.write('[\n')
        for lang, n in index:
            out.write('    [lang = %s, texts = %d],\n' % (atm_str(lang), n))
        out.write(']\n')
    for lang, n in index:
        print('%-4s %d' % (lang, n))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: po.py <source po> <destination po>')
    main(sys.argv[1], sys.argv[2])
