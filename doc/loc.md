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
| Other screens and main | 3368 | 872 | the options of Céu have 741 lines (measured with the reduced options of the first version) |

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

## Only what was ported, against the C++ of the official game

`tools/loc.py OFFICIAL CEU` counts, per unit, the files of the official
game (`Pingus/pingus@ffe3851`, `.cpp` and `.hpp`), of the Céu rewrite,
and of the port that do the same job. Lines as above, with the lines of
the preprocessor left out too; tokens are identifiers, numbers,
strings, tags, and operators, with the comments removed. Left out of
all three: the editor, the recording of demos, the add-on, font and
sprite screens, the configuration files.

| Unit | C++ lines | Céu lines | Atmos lines | C++ tokens | Céu tokens | Atmos tokens |
|------|-----------|-----------|-------------|------------|------------|--------------|
| action basher | 133 | 94 | 62 | 653 | 649 | 391 |
| action blocker | 80 | 40 | 16 | 453 | 345 | 136 |
| action bomber | 64 | 36 | 34 | 413 | 317 | 255 |
| action bridger | 192 | 134 | 47 | 929 | 954 | 292 |
| action climber | 83 | 33 | 22 | 455 | 313 | 127 |
| action digger | 93 | 52 | 39 | 453 | 374 | 236 |
| action drown | 37 | 11 | 4 | 172 | 104 | 24 |
| action exiter | 40 | 12 | 5 | 181 | 116 | 26 |
| action faller | 114 | 69 | 40 | 714 | 557 | 333 |
| action floater | 58 | 17 | 12 | 281 | 143 | 67 |
| action jumper | 41 | 28 | 11 | 230 | 237 | 84 |
| action laser_kill | 37 | 12 | 4 | 176 | 67 | 27 |
| action miner | 87 | 64 | 34 | 516 | 576 | 254 |
| action slider | 58 | 36 | 20 | 350 | 296 | 147 |
| action splashed | 38 | 13 | 6 | 184 | 105 | 35 |
| action waiter | 40 | 15 | 5 | 180 | 99 | 29 |
| action walker | 125 | 88 | 63 | 733 | 733 | 414 |
| action angel | 40 | --- | 11 | 230 | --- | 104 |
| action boarder | 71 | --- | 28 | 470 | --- | 237 |
| action smashed | 37 | --- | 4 | 177 | --- | 27 |
| action superman | 40 | --- | 8 | 218 | --- | 81 |
| pingu core | 1773 | 663 | 221 | 10047 | 5257 | 1529 |
| world objects, weather | 1767 | 744 | 540 | 13600 | 5579 | 4436 |
| game: world, panel, playfield, level, ground | 2965 | 663 | 664 | 17883 | 4914 | 4838 |
| screens: menu, start, result, story, credits, levels, worldmap | 4781 | 2409 | 832 | 27672 | 17013 | 6207 |
| **total, game logic** | **12794** | **5233** | **2732** | **77370** | **38748** | **20336** |
| options (all but the renderer) | 652 | 598 | 177 | 4811 | 4615 | 1496 |
| engine (C++ engine / Céu engine / C + Atmos) | 7838 | 532 | 1219 | 47054 | 3365 | 10335 |

17 actions in common: C++ 1320 / Céu 754 / Atmos 424 lines, 7073 / 5985 / 2877 tokens

- On the game logic, the port has 0.21x the lines and 0.26x the tokens
  of the C++, and 0.52x the lines and tokens of Céu (the Céu column is
  smaller than the C++ also because the Céu rewrite called the C++ to
  read levels, and had 17 actions and 10 objects).
- Tokens are a fairer measure than lines: the C++ splits a statement
  over more lines. By tokens, an action of the port is 0.41x its C++
  (17 actions in common) and 0.48x its Céu.
- The unit with the largest gain is the pingu core (0.15x the tokens of
  the C++): the action holder, the action names, the pingu holder,
  and the virtual dispatch of `PinguAction` become one loop of `par`
  in `Pingu`, a table of modes, and the pool `g.pingus`
  (`doc/dispatching.md`).
- The level reading of the port is in two parts: `tools/convert.py`
  turns the s-expressions into Atmos data once (380 lines of Python,
  not counted), and `X.load` reads them. The C++ counts include its
  readers (`pingus_level`, `plf_res_mgr`, `prefab_file`).
- The options are all of the official game but its choice of renderer:
  177 lines and 1496 tokens in Atmos, 0.31x the tokens of the C++.
- The engine is not like for like: the C++ engine does more (OpenGL
  renderer, GUI, input configuration, sound backends); the port has
  its C over SDL2 and the Atmos wrappers.
