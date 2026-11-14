# TODO: the port of Pingus

Everything pending in the session of the port: decisions waiting for
the author, work known and not done, reports not acknowledged, older
items. Kept current: an item leaves this file when it is done, with
the commit that did it.

The port itself is complete: the plan (P0..P9), the official data, 21
actions, the full options, the comparison with the official game (142
of 154 demos with the same trace), the benchmark.

## A. Decisions waiting for the author

1. **The workarounds the compiler no longer needs** (`ia-atmos/lang`
   `b3cf341`): `[loop=false]` is accepted, so the options `once` and
   `cycle` of `Sprite` could go back to `loop`; `"a\"b"` is accepted, so
   `'"'` could be written as in the original. `doc/compiler.md` still
   lists both as errors of the compiler.
   Waits for the author (said by the compiler session).
   *Recommended:* do it, and mark them fixed in `doc/compiler.md`, with
   the commit of the compiler.
2. **The 12 demos whose traces differ from the official game.** Late,
   small differences (one pixel, one tick, the order of deaths in a
   tick), listed in `doc/fidelity.md`.
   *Recommended:* investigate the 3 with an early difference
   (`intensiv-timpany` tick 301, `real6` 630, `stone5-grumbel` 936)
   with `PINGUS_TRACE=2` in both games; leave the rest.
3. **A line in `doc/bench.md` for the new compiler** (`b3cf341`): the
   same results, no measurable difference in speed or memory (noise of
   about 10%), binary 8 KB smaller.
   *Recommended:* add it, two lines.

4. **Expressiveness over exactness, after full fidelity** (a rule of
   the author for every port, relayed by the compiler session): once a
   port is identical to its original on its runs, it may relax the
   exactness in favor of expressiveness, if the intent of the original
   author stays. Until then, a difference is a defect. This port is not
   there yet: 142 of the 154 demos that the official game plays give the
   same trace, 12 differ (A.2), 5 cannot be compared. An option, not a
   task. Candidates, the four places that read poorly because they copy
   the original (objects that poll every tick, the order of reactions in
   a tick by the order of spawns, the teleporter writing a position,
   clocks by arithmetic), and the floats of 32 bits.
   *Recommended:* first decide A.2 (whether to reach 154 of 154, or
   accept the 12 as the limit); then tag the faithful commit, and relax
   in small commits, each with what it gives up and gains, the outputs
   replaced in the same commit, and a document of the deliberate
   differences; never mixed with the move to `env-sdl` (B.11), which
   must keep the outputs identical. Ask the author what to relax before
   a large change.

## B. Work known and not done

0. The remote of the checkout still has the old address
   (`fsantanna/ceu-atmos-pingus`); GitHub redirects the pushes.
   Changing it (`git remote set-url origin
   https://github.com/ia-atmos/sdl-pingus`) was refused by the
   permissions of the session: the author may do it, or allow it.

1. Input configuration and controllers: the only unchecked item of the
   README; the keys of the original are fixed in `game/game.atm`.
2. Drawing offsets: the bridger (`get_look` of the original, about 25
   lines) and the center of the climber (`doc/todo.md`).
3. The worldmap: fast forward, and its border (open in `doc/todo.md`).
4. A test of blocker, faller, blocker (`doc/todo.md`, partly).
5. Fullscreen and resolution were tested only with the test driver,
   which keeps the window at 800x600: not seen on a real screen.
6. The languages in the options are in the order of their codes; the
   original sorts them by name.
7. `doc/fidelity.md`: its first table counts the solved demos of
   `tst/demos.sh` as 10; it is 12 now. Its count of solved levels names
   10.
8. `doc/bench.md`: says that fast forward is "5 ticks per frame", while
   the code runs 4 ticks per 20 ms: to check. A fast forward run by
   `PINGUS_KEYS` gave the same frames as without it: to check that the
   key of the script works.
9. The 5 demos that the official game cannot load (`crystal-10-rz`,
   `desert5-tflavel-original`, `egypts1-judit`, `hellmouth-23-rz+eriksoe`,
   `hellmouth-24-rz`): no comparison for them.
10. Language features that would help, for the compiler (sent in the
    session): guarded awaits over a pool (objects poll every tick), an
    explicit order of reactions in a tick (`:tick`/`:tock`, the order of
    spawns), a single writer of a pingu (the teleporter writes its
    position), clocks as values (timings by arithmetic), `f32`. None is
    asked; the port works around them.

11. **Work to come: the shared environment `ia-atmos/env-sdl`** (plan:
    `ia-atmos/lang`, `.claude/plans/261113-env-sdl.md`; written by the
    session `env-sdl`). The three games over SDL (this one, SNKRX,
    Flare) will use it instead of a platform layer of their own. First,
    that session inventories `engine/sdl.atm` and `engine/pingus.h` and
    may ask what a function is for: answer it. Later, when it has what
    Pingus needs, move the platform part of the layer there (driver,
    images, fonts, sounds, test mode), with the 159 traces identical;
    Pingus is planned to be the first. What is of the game stays here:
    the ground and collision maps and the mover in C.

## C. Reported, not acknowledged

1. The full options (commits `4280bbe` to `32a88e7`): all the options
   of the official game but its renderer; "Reset to defaults" is not in
   the official game either (commented out there).
2. The run of the port with the compiler `b3cf341`: tests, ASAN, the
   159 traces byte-identical, the benchmark unchanged (sent to the
   compiler session and to the author).
3. The tips for a port of SuperTux (sent to the compiler session).

## D. Older items

1. `doc/fidelity.md`: the counts between 39 and 142 identical traces
   were not recorded; only the measured ones are in the table.
2. The address of the compiler: `../fsantanna/ceu-atmos` in this
   container, a checkout of `main`; `run.sh` finds it by its former
   names too.
3. Done: the names of the repositories (`ia-atmos/sdl-pingus`,
   `ia-atmos/lang`, the link of the plan) in `run.sh`, `README.md`,
   `doc/compiler.md`, `tools/bench/README.md`.
