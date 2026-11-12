# ceu-atmos-pingus

Pingus in [Atmos](https://github.com/fsantanna/ceu-atmos): a port of
[Pingus](https://pingus.seul.org/), a free puzzle game by Ingo Ruhnke
and others, to a language of structured synchronous concurrency.

- The target of the port is the 2018 rewrite of the game logic from
  C++ to Céu ([fsantanna/pingus@036852a][ceu]), the case study
  "Structured Synchronous Reactive Programming for Game Development:
  On Rewriting Pingus from C++ to Céu" (SBGames 2018).
- The port is a third point for that study: C++, Céu, Atmos. See
  [doc/](doc/README.md).
    - The control-flow patterns of the study are the design rule.
    - No state variables for control: no flags, phase enums, or frame
      counters ([doc/state.md](doc/state.md)).
    - The data of the game is Atmos data, read with `X.load`, instead
      of s-expressions with their own reader.

The plan, with the settled decisions and the milestones, is in
[fsantanna/ceu-atmos][plan].

[ceu]:  https://github.com/fsantanna/pingus/tree/036852a7718d860baaf2db33cb8c469043df0253
[plan]: https://github.com/fsantanna/ceu-atmos/blob/ccr-566b5373-ag7186/.claude/plans/261110-pingus.md

## Run

It requires a checkout of [ceu-atmos](https://github.com/fsantanna/ceu-atmos),
built with `make`, next to this one (`../ceu-atmos`), or its compiler
in `ATMOS`; and the development files of SDL2, SDL2_image, and
SDL2_mixer:

```
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev
./run.sh                                    # the menu
./run.sh main.atm data/levels/tutorial/snow7-grumbel.pingus.atm
./run.sh main.atm data/worldmaps/tutorial.worldmap.atm
./run.sh -o pingus main.atm                 # builds only
```

Keys in a level: `P` pause, `S` single step, `F` or `Space` fast
forward (hold), `A` armageddon, `1` to `0` the actions, arrows to
scroll, `Escape` to quit; the right button drags the view. `F5` shows
the options anywhere. The progress is saved in `~/.pingus-atmos.atm`
(or in `$PINGUS_HOME`).

## Layout

```
main.atm            the sequence of screens
engine/             the engine
    pingus.h        C: driver, images, fonts, sounds, ground maps
    sdl.atm         the Atmos functions over it
    engine.atm      sprites (a task each), fonts, mouse, widgets
game/               the game screen
    game.atm        layers, clock, pause, armageddon, goal
    hud.atm         buttons, counters, time, small map
    playfield.atm   the view, clicks on pingus
    level.atm       levels, prefabs, groups
    ground.atm      groundpieces
    pingu/          the Pingu task, the mover, particles
        actions/    one file per action (21)
    objs/           one file per object (10 of Céu), extra.atm (12 more)
screens/            menu, start, result, story, credits, levels,
                    worldmap, options
data/               converted data, images, sounds, music
tools/convert.py    s-expressions to Atmos data, with its checks
tools/check.atm     loads every data file with X.load
tools/measure.py    peak memory and CPU of a run
tools/compare.sh    a demo of the original in both games, the traces compared
tools/bench/        the patch of the official game for the comparisons
tst/                tests with no screen
doc/                the case study: C++, Céu, Atmos
```

## Data

The data files of the game are in `data/`, as Atmos data
(`*.pingus.atm`, `*.sprite.atm`, ...). They are generated, once, from
the s-expression files of the 2018 repository (images and sprite
descriptions) and of the official game (levels, levelsets, worldmaps,
prefabs, stories):

```
git clone https://github.com/fsantanna/pingus /tmp/pingus
git -C /tmp/pingus checkout 036852a
git clone https://github.com/Pingus/pingus /tmp/official
git -C /tmp/official checkout ffe3851
tools/merge-data.sh /tmp/pingus/data /tmp/official/data /tmp/src
tools/convert.py /tmp/src data
tools/po.py /tmp/pingus/data/po data/po
```

The header of `tools/convert.py` describes the mapping and what the
conversion loses. `data/levels.atm` is the index of the levels, with
the objects and actions that each one needs: the game offers only the
levels it supports (522 of 523; the last one needs a rocket launcher,
which no version of the game has).

## Test

```
tst/run.sh              # all tests, about 1 minute
tst/run.sh update       # stores the new outputs as the expected ones
ASAN=1 tst/run.sh       # with the address sanitizer and leak checks
tst/play.sh LEVEL FRAMES [ORDERS] [KEYS]    # one level, with its trace
```

All with no screen (`SDL_VIDEODRIVER=dummy`), fixed frames of 25ms, a
fixed random seed, and scripted keys and mouse:

- the data: every converted file loads with `X.load`;
- the engine: a sprite, a text, and a scripted click;
- screenshots of the menu, the levelsets, the start screen, and a game,
  compared with `tst/shots/`;
- the game played with the mouse only (`tst/clicks.sh`);
- 25 scripted levels (`tst/levels.txt`), one per action and per object,
  whose traces of actions are compared with `tst/golden/`.

## Status

- [x] P0 Groundwork: license, converter, data, report of levels
- [x] P1 Engine
- [x] P2 Menus
- [x] P3 Story, credits, worldmap
- [x] P4 Ground
- [x] P5 Pingu core
- [x] P6 Actions and traps
- [x] P7 The rest of the game: pause, fast forward, options, progress
- [x] P8 Case study ([doc/](doc/README.md)), with the benchmark against
      the official game ([doc/bench.md](doc/bench.md))
- [x] P9 Later items: the 12 objects and 4 actions that Céu did not have
- [x] The levels of the official game, and its timings: compared tick by
      tick on its demos, 142 of 154 with the same trace
      ([doc/fidelity.md](doc/fidelity.md))
- [x] Translations: the `.po` files of the game, chosen in the options
- [x] The options of the official game (all but its choice of renderer)
- [ ] Input configuration, controllers

## License

Pingus is free software under the GNU General Public License, version
3 or later (see `LICENSE`), and this port is a derivative work under
the same license.

- The authors of the game, of its images, levels, sounds, and music
  are in `AUTHORS` and in `data/credits/`, and in the READMEs of
  `data/`.
- The Céu rewrite is by Francisco Sant'Anna.
