# Lines of code

Lines that are not blank nor comments, per part, in the Céu rewrite
(`ceu/` of `fsantanna/pingus@036852a`) and in this port. Measured with:

```
grep -v '^\s*$' FILES | grep -v '^\s*;;' | wc -l     # Atmos
grep -v '^\s*$' FILES | grep -v '^\s*//' | wc -l     # Céu, C
```

| Part | Céu | Atmos | Notes |
|------|-----|-------|-------|
| Engine: sprites, surfaces, widgets, driver | 528 | 407 | Céu calls 22k lines of C++ for the display; Atmos has its own C (below) |
| Pingu core: pingu, mover, codes, particles | 517 | 214 | |
| Pingu actions (17) | 879 | 423 | |
| World objects (10 of Céu) | 864 | 223 | Céu has C++ in native blocks for the reading of the data |
| World objects (12 new) | --- | 315 | not in the Céu rewrite |
| Game screen: game, panel, playfield, level | 937 | 607 | |
| Other screens and main | 3368 | 872 | the options of Céu have 741 lines; the port has a reduced one |

The C of the port, which takes the place of the C++ that the Céu code
called (display, fonts, sounds, collision and ground maps):

| | Lines |
|-|-------|
| `engine/pingus.h` | 727 |
| C++ called by the Céu code (`src/`, see the plan) | 22106 |

The data converter (`tools/convert.py`, Python) has 380 lines, and
replaces the s-expression reader (936 lines of C++) and the readers of
each kind of file.

## Notes

- The Céu rewrite was a partial port: the game logic in Céu, with the
  C++ of the original for the rest. The port is complete: the engine
  is in C and Atmos, over SDL2.
- The lines of the game logic in Atmos are about half of the ones in
  Céu. Most of the difference is in the reading of the data (a native
  C++ reader in Céu, tables of `X.load` in Atmos), the declarations of
  types (`data`, `var&`, aliases), and the RRect layout system of Céu,
  which Atmos does not need.
