# TODO: the port of Pingus

Everything pending in the session of the port: decisions waiting for
the author, work known and not done, reports not acknowledged, older
items. Kept current: an item leaves this file when it is done, with
the commit that did it.

The port itself is complete: the plan (P0..P9), the official data, 21
actions, the full options, the comparison with the official game (142
of 154 demos with the same trace), the benchmark.

## A. Decisions waiting for the author

1. **The name of the compiler in the port.** The compiler moved from
   `fsantanna/ceu-atmos` to `ia-atmos/lang`. Places: `run.sh` (looks for
   `../ceu-atmos` and `../fsantanna/ceu-atmos`), `README.md` (links,
   and the link of the plan, which points to the old branch
   `ccr-566b5373-ag7186`; the plan is now in `ia-atmos/lang`, `main`,
   `.claude/plans/261110-pingus.md`), `doc/compiler.md`.
   This repository moved too: `fsantanna/ceu-atmos-pingus` is now
   `ia-atmos/pingus` (GitHub redirects pushes; the remote of the
   checkout still has the old address).
   *Recommended:* wait for the renaming of the repositories of the
   organization (this one may become `sdl-pingus`), and update all the
   names, and the remote, in one commit then.
2. **The workarounds the compiler no longer needs** (`ia-atmos/lang`
   `b3cf341`): `[loop=false]` is accepted, so the options `once` and
   `cycle` of `Sprite` could go back to `loop`; `"a\"b"` is accepted, so
   `'"'` could be written as in the original. `doc/compiler.md` still
   lists both as errors of the compiler.
   *Recommended:* do it with item 1, and mark them fixed in
   `doc/compiler.md`, with the commit of the compiler.
3. **The 12 demos whose traces differ from the official game.** Late,
   small differences (one pixel, one tick, the order of deaths in a
   tick), listed in `doc/fidelity.md`.
   *Recommended:* investigate the 3 with an early difference
   (`intensiv-timpany` tick 301, `real6` 630, `stone5-grumbel` 936)
   with `PINGUS_TRACE=2` in both games; leave the rest.
4. **A line in `doc/bench.md` for the new compiler** (`b3cf341`): the
   same results, no measurable difference in speed or memory (noise of
   about 10%), binary 8 KB smaller.
   *Recommended:* add it, two lines.

## B. Work known and not done

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

## C. Reported, not acknowledged

1. The full options (commits `4280bbe` to `32a88e7`): all the options
   of the official game but its renderer; "Reset to defaults" is not in
   the official game either (commented out there).
2. The run of the port with the compiler `b3cf341`: tests, ASAN, the
   159 traces byte-identical, the benchmark unchanged (sent to the
   compiler session and to the author).
3. The tips for a port of SuperTux (sent to the compiler session).
4. The question of item A.1 (now or with the renaming), asked of the
   author, not answered.

## D. Older items

1. `doc/fidelity.md`: the counts between 39 and 142 identical traces
   were not recorded; only the measured ones are in the table.
2. The address of the compiler: `../fsantanna/ceu-atmos` in this
   container, a checkout of `main`.
