# ceu-atmos-pingus

Pingus in [Atmos](https://github.com/fsantanna/ceu-atmos): a port of
the game logic of [Pingus](https://pingus.seul.org/), a free puzzle
game by Ingo Ruhnke and others.

- The target of the port is the 2018 rewrite of the game logic from
  C++ to Céu ([fsantanna/pingus@036852a][ceu]), the case study
  "Structured Synchronous Reactive Programming for Game Development:
  On Rewriting Pingus from C++ to Céu" (SBGames 2018).
- The port is a third point for that study: C++, Céu, Atmos.
    - The control-flow patterns of the study are the design rule.
    - No state variables for control: no flags, phase enums, or frame
      counters.
    - The data of the game is Atmos data, read with `X.load`, instead
      of s-expressions with their own reader.

The plan, with the settled decisions and the milestones, is in
[fsantanna/ceu-atmos][plan].

**Work in progress**: see [Status](#status).

[ceu]:  https://github.com/fsantanna/pingus/tree/036852a7718d860baaf2db33cb8c469043df0253
[plan]: https://github.com/fsantanna/ceu-atmos/blob/ccr-566b5373-ag7186/.claude/plans/261110-pingus.md

## Layout

```
data/               converted data, images, sounds, music
tools/convert.py    s-expressions to Atmos data, with its checks
tools/check.atm     loads every data file with `X.load`
```

## Data

The data files of the game are in `data/`, as Atmos data
(`*.pingus.atm`, `*.sprite.atm`, ...). They are generated, once, from
the s-expression files of the 2018 repository:

```
git clone https://github.com/fsantanna/pingus /tmp/pingus
git -C /tmp/pingus checkout 036852a
tools/convert.py /tmp/pingus/data data
find data -name '*.atm' > /tmp/files.txt
atmos tools/check.atm /tmp/files.txt
```

The header of `tools/convert.py` describes the mapping and what the
conversion loses. `data/levels.atm` is the index of the levels, with
the objects and actions that each one needs.

## Status

- [ ] P0 Groundwork
- [ ] P1 Engine
- [ ] P2 Menus
- [ ] P3 Story, credits, worldmap
- [ ] P4 Ground
- [ ] P5 Pingu core
- [ ] P6 Actions and traps
- [ ] P7 The rest of the game
- [ ] P8 Case study
- [ ] P9 Later items

## License

Pingus is free software under the GNU General Public License, version
3 or later (see `LICENSE`), and this port is a derivative work under
the same license.

- The authors of the game, of its images, levels, sounds, and music
  are in `AUTHORS` and in `data/credits/`.
- The Céu rewrite is by Francisco Sant'Anna.
