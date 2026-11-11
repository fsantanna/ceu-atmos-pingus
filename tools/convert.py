#!/usr/bin/env python3

# One-time converter of the data of Pingus, from s-expressions to
# Atmos data, which the game reads with `X.load`.
#
#   tools/convert.py <data of fsantanna/pingus@036852a> <data of the port>
#
# Reads every s-expression file in the source (levels, demos, sprites,
# prefabs, levelsets, worldmaps, stories, controllers, fonts), and
# writes `<file>.atm` in the same relative path of the destination.
# Then it checks the result:
#
#   - the number of files per kind is the expected one;
#   - every file converts back to the original s-expression (round
#     trip), up to what is listed in "Losses" below;
#   - no two fields of a table collide after the renaming.
#
# It also writes `levels.atm`, the index of the levels: the objects
# and actions that each one needs, and whether the game supports it.
#
# That every converted file loads with `X.load` is checked apart, by
# `tools/check.atm`, since it needs the compiler.
#
# Mapping:
#
#   (pingus-level ...)              :pingus.level [...]
#   (name v)                        name = v            (`-` becomes `_`)
#   (name a b c)                    name = [a, b, c]
#   (name)                          name = []
#   (name (k v) ...)                name = [k=v, ...]
#   (objects (groundpiece ...) ...) objects = [:groundpiece [...], ...]
#   (position 1 2 3), in a list     :position [1, 2, 3]
#   #t  #f                          true  false
#   "ROT90", in an enumeration      :ROT90
#   sdl:keyboard-button             :sdl.keyboard_button
#   a file with many expressions    [:level [...], :pingu_action [...]]
#
# Losses, which the round trip sets aside:
#
#   - spacing and comments;
#   - `_` and `-` in names are the same (`laser_exit`, `intro-story`);
#   - a field that appears twice in a table keeps its first value;
#   - a bare symbol as a value becomes a string;
#   - the lexeme of a number (`.5` is `0.5`).

import os
import re
import sys

KINDS = {
    '.pingus':      447,
    '.pingus-demo': 159,
    '.sprite':      362,
    '.prefab':       17,
    '.levelset':     15,
    '.worldmap':      2,
    '.story':         2,
    '.scm':           5,
    '.font':          5,
}

# Names whose sublists are a sequence of objects, not fields.
LISTS = {
    'objects', 'pages', 'levels', 'nodes', 'edges', 'positions',
    'images', 'glyphs',
}

# Fields whose strings are enumerations.
ENUMS = { 'modifier', 'type', 'direction', 'origin', 'action' }

# What the first version of the game implements.
OBJECTS = {
    'entrance', 'exit', 'groundpiece', 'guillotine', 'hotspot',
    'laser_exit', 'liquid', 'smasher', 'spike', 'surface_background',
}
ACTIONS = {
    'basher', 'blocker', 'bomber', 'bridger', 'climber', 'digger',
    'floater', 'jumper', 'miner', 'slider',
}

ID  = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
NUM = re.compile(r'^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$')

class Sym (str):
    pass

###############################################################################
# S-EXPRESSIONS
###############################################################################

# A file as a list of expressions. An expression is a list, a `Sym`, a
# `str`, a number, or a boolean.
def sexp_read (src):
    stack = [[]]
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in ' \t\r\n':
            i += 1
        elif c == ';':
            while i < n and src[i] != '\n':
                i += 1
        elif c == '(':
            stack.append([])
            i += 1
        elif c == ')':
            x = stack.pop()
            stack[-1].append(x)
            i += 1
        elif c == '"':
            out = []
            i += 1
            while src[i] != '"':
                if src[i] == '\\':
                    i += 1
                    out.append({'n':'\n', 't':'\t'}.get(src[i], src[i]))
                else:
                    out.append(src[i])
                i += 1
            i += 1
            stack[-1].append(''.join(out))
        else:
            j = i
            while j < n and src[j] not in ' \t\r\n()";':
                j += 1
            tk = src[i:j]
            i = j
            if tk == '#t':
                stack[-1].append(True)
            elif tk == '#f':
                stack[-1].append(False)
            elif NUM.match(tk):
                f = float(tk)
                isint = re.match(r'^[-+]?\d+$', tk)
                stack[-1].append(int(tk) if isint else f)
            else:
                stack[-1].append(Sym(tk))
    assert len(stack) == 1, 'unbalanced parentheses'
    return stack[0]

def sexp_write (x, ind=0):
    if isinstance(x, list):
        if all(not isinstance(v,list) for v in x):
            return '(' + ' '.join(sexp_write(v) for v in x) + ')'
        sp = '\n' + ' '*(ind+2)
        return '(' + sexp_write(x[0]) + ''.join(
            (sp if isinstance(v,list) else ' ') + sexp_write(v,ind+2)
                for v in x[1:]
        ) + ')'
    elif isinstance(x, Sym):
        return x
    elif isinstance(x, bool):
        return '#t' if x else '#f'
    elif isinstance(x, str):
        return '"' + x.replace('\\','\\\\').replace('"','\\"') \
                      .replace('\n','\\n') + '"'
    else:
        return repr(x)

###############################################################################
# ATMOS DATA: a tagged table is `Tab`, with `tag`, positional `vec`, and
# named `map` (a list of pairs, to keep the order).
###############################################################################

class Tab:
    def __init__ (self, tag=None):
        self.tag = tag
        self.vec = []
        self.map = []

class Tag (str):
    pass

def name_to_atm (s):
    return s.replace('-', '_')

def tag_to_atm (s, top):
    if top and s.startswith('pingus-'):
        s = 'pingus.' + s[len('pingus-'):]
    return s.replace('-', '_').replace(':', '.')

def is_scalar (v):
    return not isinstance(v, list)

def scalar_to_atm (v, name):
    if isinstance(v, Sym):
        v = str(v)
    if isinstance(v, str) and (name in ENUMS) and ID.match(v):
        return Tag(v)
    return v

# `(head ...)` as an object: a tagged table.
def obj_to_atm (x, top, path):
    assert x and isinstance(x[0], Sym), (path, 'object with no head')
    t = Tab(tag_to_atm(x[0], top))
    body_to_atm(t, x[0], x[1:], path+'/'+x[0])
    return t

# The contents of a list into `t`: scalars are positional, sublists are
# fields.
def body_to_atm (t, name, rest, path):
    if all(is_scalar(v) for v in rest):
        t.vec = [ scalar_to_atm(v,name) for v in rest ]
    else:
        assert all(not is_scalar(v) for v in rest), (path, 'mixed contents')
        if (name in LISTS) or any(':' in v[0] for v in rest):
            t.vec = [ obj_to_atm(v,False,path) for v in rest ]
        else:
            seen = set()
            for v in rest:
                assert v and isinstance(v[0], Sym), (path, 'field with no name')
                k = name_to_atm(v[0])
                if v[0] in seen:
                    continue                    # loss: the first one stays
                assert k not in seen, (path, 'name collision', k)
                assert k != 'tag', (path, 'field `tag`')
                seen.add(v[0])
                seen.add(k)
                t.map.append((k, field_to_atm(v[0], v[1:], path+'/'+v[0])))

def field_to_atm (name, rest, path):
    if len(rest)==1 and is_scalar(rest[0]):
        return scalar_to_atm(rest[0], name)
    t = Tab()
    body_to_atm(t, name, rest, path)
    return t

def file_to_atm (exprs, path):
    if len(exprs)==1 and exprs[0][0].startswith('pingus-'):
        return obj_to_atm(exprs[0], True, path)
    t = Tab()
    t.vec = [ obj_to_atm(x,False,path) for x in exprs ]
    return t

def atm_str (s):
    out = []
    for c in s:
        if   c == '\n': out.append('\\n')
        elif c == '\t': out.append('\\t')
        elif c == '\r': out.append('\\r')
        elif c == '"':  out.append('\\x22')
        elif c == '\\': out.append('\\\\')
        elif ord(c) < 32:
            out.append('\\x%02X' % ord(c))
        else:
            out.append(c)
    return '"' + ''.join(out) + '"'

def atm_num (v):
    if isinstance(v, int):
        return str(v)
    s = repr(v)
    if ('e' in s) or ('inf' in s) or ('nan' in s):
        s = '%.10f' % v
    return s

def atm_write (v, ind=0):
    if isinstance(v, Tab):
        pre = (':' + v.tag + ' ') if v.tag else ''
        items = [ atm_write(x,ind+4) for x in v.vec ] + \
                [ k + ' = ' + atm_write(x,ind+4) for k,x in v.map ]
        flat = pre + '[' + ', '.join(items) + ']'
        simple = all(not isinstance(x,Tab) or (not x.map and not x.tag and
            all(not isinstance(y,Tab) for y in x.vec))
                for x in v.vec + [x for _,x in v.map])
        if not items or (simple and len(flat)+ind <= 78 and '\n' not in flat):
            return flat
        sp = '\n' + ' '*(ind+4)
        return pre + '[' + ''.join(sp + i + ',' for i in items) + \
               '\n' + ' '*ind + ']'
    elif isinstance(v, Tag):
        return ':' + v
    elif isinstance(v, bool):
        return 'true' if v else 'false'
    elif isinstance(v, str):
        return atm_str(v)
    else:
        return atm_num(v)

# Reads back what `atm_write` writes (and no more than that).
def atm_read (src):
    pos = [0]
    TK = re.compile(r'''\s*(?:
        (?P<str>"(?:[^"\\]|\\.)*") |
        (?P<tag>:[A-Za-z0-9_.]+)   |
        (?P<num>-?\d[0-9.]*)       |
        (?P<id>[A-Za-z_][A-Za-z0-9_]*) |
        (?P<sym>[\[\],=])
    )''', re.X)
    def nxt (peek=False):
        m = TK.match(src, pos[0])
        assert m, ('invalid data', src[pos[0]:pos[0]+40])
        if not peek:
            pos[0] = m.end()
        return m.lastgroup, m.group(m.lastgroup)
    def unstr (s):
        def f (m):
            c = m.group(1)
            if c[0] == 'x':
                return chr(int(c[1:],16))
            return {'n':'\n', 't':'\t', 'r':'\r', '\\':'\\'}[c]
        return re.sub(r'\\(x[0-9A-Fa-f]{2}|.)', f, s[1:-1])
    def value ():
        k, s = nxt()
        if k == 'str':
            return unstr(s)
        elif k == 'num':
            return float(s) if '.' in s else int(s)
        elif k == 'id':
            return {'true':True, 'false':False}[s]
        elif k == 'tag':
            if nxt(True) == ('sym','['):
                nxt()
                return table(s[1:])
            return Tag(s[1:])
        else:
            assert s == '[', ('invalid data', s)
            return table(None)
    def table (tag):
        t = Tab(tag)
        while True:
            k, s = nxt(True)
            if (k,s) == ('sym',']'):
                nxt()
                return t
            if k == 'id' and s not in ('true','false'):
                nxt()
                assert nxt() == ('sym','=')
                t.map.append((s, value()))
            else:
                t.vec.append(value())
            k, s = nxt()
            if (k,s) == ('sym',']'):
                return t
            assert (k,s) == ('sym',','), ('invalid data', s)
    v = value()
    assert src[pos[0]:].strip() == '', 'garbage after the value'
    return v

###############################################################################
# BACK TO S-EXPRESSIONS, and the comparison of the round trip.
###############################################################################

def name_to_sexp (s):
    return Sym(s.replace('_', '-'))

def tag_to_sexp (s):
    if s.startswith('pingus.'):
        s = 'pingus-' + s[len('pingus.'):]
    return Sym(s.replace('_', '-').replace('.', ':'))

def scalar_to_sexp (v):
    return str(v) if isinstance(v, Tag) else v

def body_to_sexp (t):
    return [ obj_to_sexp(v) if isinstance(v,Tab) else scalar_to_sexp(v)
                for v in t.vec ] + \
           [ field_to_sexp(k,v) for k,v in t.map ]

def obj_to_sexp (t):
    return [tag_to_sexp(t.tag)] + body_to_sexp(t)

def field_to_sexp (k, v):
    if isinstance(v, Tab):
        return [name_to_sexp(k)] + body_to_sexp(v)
    return [name_to_sexp(k), scalar_to_sexp(v)]

def file_to_sexp (v):
    if v.tag:
        return [ obj_to_sexp(v) ]
    return [ obj_to_sexp(x) for x in v.vec ]

# The original, with the accepted losses applied.
def normal (x):
    if isinstance(x, list):
        head = Sym(x[0].replace('_', '-'))
        rest = x[1:]
        isfld = all(not is_scalar(v) for v in rest) and rest and \
            not ((x[0] in LISTS) or any(':' in v[0] for v in rest))
        if isfld:
            seen, out = set(), []
            for v in rest:
                if v[0] not in seen:
                    seen.add(v[0])
                    out.append(v)
            rest = out
        return [head] + [ normal(v) for v in rest ]
    elif isinstance(x, Sym):
        return str(x)
    return x

def same (a, b):
    if isinstance(a, list) or isinstance(b, list):
        return isinstance(a, list) and isinstance(b, list) and \
            len(a) == len(b) and all(same(x,y) for x,y in zip(a,b))
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int,float)) and isinstance(b, (int,float)):
        return abs(a-b) <= 1e-9 * max(1, abs(a), abs(b))
    return type(a) == type(b) and a == b

###############################################################################
# INDEX OF THE LEVELS
###############################################################################

def field (t, k):
    for k1, v in t.map:
        if k1 == k:
            return v
    return None

# The kinds of objects that a list of objects needs, with prefabs and
# groups resolved.
def kinds_of (objs, prefabs, out):
    for o in (objs.vec if isinstance(objs,Tab) else []):
        if o.tag == 'group':
            kinds_of(field(o,'objects'), prefabs, out)
        elif o.tag == 'prefab':
            name = field(o, 'name')
            if name in prefabs:
                kinds_of(field(prefabs[name],'objects'), prefabs, out)
            else:
                out.add('prefab?' + str(name))
        else:
            out.add(o.tag)

def index (levels, prefabs):
    root = Tab('pingus.levels')
    for path in sorted(levels):
        lvl = levels[path]
        objs = set()
        kinds_of(field(lvl,'objects'), prefabs, objs)
        head = field(lvl, 'head')
        acts = field(head, 'actions') if head else None
        acts = { k for k,_ in acts.map } if isinstance(acts,Tab) else set()
        miss = sorted((objs - OBJECTS) | (acts - ACTIONS))
        t = Tab()
        t.map.append(('file', path))
        t.map.append(('ok', not miss))
        for k, vs in (('objects',objs), ('actions',acts), ('missing',miss)):
            v = Tab()
            v.vec = [ Tag(x) if ID.match(x) else x for x in sorted(vs) ]
            t.map.append((k, v))
        root.vec.append(t)
    return root

###############################################################################
# MAIN
###############################################################################

def main (src, dst):
    counts  = { k:0 for k in KINDS }
    levels  = {}
    prefabs = {}
    for dir, _, files in sorted(os.walk(src)):
        for f in sorted(files):
            ext = os.path.splitext(f)[1]
            if ext not in KINDS:
                continue
            counts[ext] += 1
            rel = os.path.relpath(os.path.join(dir,f), src)
            with open(os.path.join(src,rel), encoding='utf-8') as fd:
                exprs = sexp_read(fd.read())
            out = atm_write(file_to_atm(exprs, rel)) + '\n'

            # round trip, from the text that is written
            back = atm_read(out)
            a = file_to_sexp(back)
            b = [ normal(x) for x in exprs ]
            assert same(a, b), (rel, 'round trip')

            os.makedirs(os.path.dirname(os.path.join(dst,rel)), exist_ok=True)
            with open(os.path.join(dst,rel+'.atm'), 'w', encoding='utf-8') as fd:
                fd.write(out)

            if ext == '.pingus':
                levels[rel+'.atm'] = back
            elif ext == '.prefab':
                prefabs[rel[:-len('.prefab')]] = back

    for k, n in KINDS.items():
        assert counts[k] == n, ('count', k, counts[k], n)

    idx = index(levels, prefabs)
    with open(os.path.join(dst,'levels.atm'), 'w', encoding='utf-8') as fd:
        fd.write(atm_write(idx) + '\n')

    ok = sum(1 for t in idx.vec if field(t,'ok'))
    print('files   :', sum(counts.values()))
    for k, n in counts.items():
        print('   %-13s %d' % (k, n))
    print('levels  : %d supported, %d not' % (ok, len(idx.vec)-ok))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: convert.py <source data> <destination data>')
    main(sys.argv[1], sys.argv[2])
