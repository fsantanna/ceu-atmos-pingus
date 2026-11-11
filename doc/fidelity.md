# Fidelity: the demos of the original

The data of Pingus has 159 demos (`*.pingus-demo`): recordings of the
actions given to the pingus, by tick of the world and by pingu, most of
them solving their level. `tools/demo.py` turns a demo into the orders
of the test mode of the port, and `tst/demos.sh` replays them all and
counts the levels still solved.

| Build | Solved | Failed | No result |
|-------|--------|--------|-----------|
| first version (release every `rate` ticks, exits before the pingus) | 8 | 82 | 69 |
| release every `rate + 1` ticks, objects behind the pingus react after them (`:tock`), orders of the same tick together, two Escapes to end | 10 | 143 | 6 |
| landing in the same tick as the collision, velocities clamped | 10 | 143 | 6 |

Solved now: the bomber, bridger, climber, digger and miner tutorials,
`crystal2`, `crystalcave3-gunter`, `hellmouth04-grumbel`,
`hellmouth10-grumbel`, `panic-cbrucher`.

A demo replays only if the game is the same, tick by tick: one pingu one
pixel off at the time of a click misses the click.

## Tick by tick against the official game

The official game, `Pingus/pingus` at `ffe3851`, builds in the
container (see `tools/bench/README.md`), with a patch
(`tools/bench/official.patch`) that prints the same trace as the port
(`PINGUS_TRACE=1`: a line per change of action, `time pingu id action
x y`), and plays demos at 100 updates per frame. `tools/compare.sh`
replays a demo in both and compares the traces; `tools/compare-all.sh`
does it for all 159 demos. `PINGUS_TRACE=2` with `PINGUS_TRACE_ID`
prints one pingu each tick, in both, to find the first tick where they
differ.

| Build | Same trace | Differ | Official cannot load |
|-------|-----------|--------|----------------------|
| first comparison (fixes above) | 17 | 137 | 5 |
| float mover, real object positions, orders after the tick | 98 | 56 | 5 |
| timings of digger, miner, basher, bridger, bomber, waiter, slider | 125 | 29 | 5 |
| forced actions, the change rules of the official game, ice, spike | 138 | 16 | 5 |
| teleporters every tick, objects in the order of their depth | **142** | 12 | 5 |

So 142 of the 154 demos that the official game plays give the same
trace in the port: every pingu, every change of action, at the same
tick and the same pixel, up to the tick 39000.

The 12 left differ late, and by one pixel or one tick (the time of the
first difference, out of the length of the trace):

| Demo | First difference |
|------|------------------|
| aliens4-phil | tick 6611, a death one pixel and one tick off |
| aliens6-phil | tick 1415, the order of two deaths in the same tick |
| hellmouth05-grumbel | tick 1265, a death 8 pixels higher |
| indiana-yingwan | tick 1116, a splash the port does not have |
| intensiv-timpany | tick 301, a death one pixel higher |
| pacman3-yingwan | tick 5109, the order of deaths in the same tick |
| pingusworld3-pacho | tick 11626, one walker of 85 |
| real6 | tick 630, a splash one tick and one pixel later |
| snow1 | tick 2105, a death one tick earlier |
| stone-castle-timpany | tick 1105, a splash the official game does not have |
| stone5-grumbel | tick 936, a walker the official game does not have |
| xmas-blockblow-timpany | tick 1627, deaths in another order |

Most are the order of the pingus killed in the same tick by the same
object, or a fall that ends one pixel apart, from the details of the
float arithmetic of the faller and of the ground removed by bombers.

The 5 demos the official game does not load (`crystal-10-rz`,
`desert5-tflavel-original`, `egypts1-judit`, `hellmouth-23-rz+eriksoe`,
`hellmouth-24-rz`) name levels or objects it no longer has.

## What the comparison found

Read in the official code first:

- an entrance releases a pingu when the time is *past* the last release
  plus the rate: one every `rate + 1` ticks;
- in a tick, the pingus move first, then the objects react (exits,
  traps), so the objects drawn behind the pingus use a second phase,
  `:tock`;
- a faller decides how it lands in the tick of the collision (the Céu
  rewrite waited one tick, as a workaround), and the velocities are
  clamped to the terminal velocity.

Found with the traces of both games:

- positions and velocities are `float` (32 bits): the mover is in C
  (`pg_move`), and gravity accumulates in `float`, as the original;
- objects are at their real positions (the conversion had rounded
  them), and are set up in the order of their depth, which decides
  which of two objects acts first on a pingu in a tick;
- the orders of the player apply after the objects of the tick;
- exits and traps force an action (`:pingu.set`), while the player
  and the armageddon request one (`:pingu.go`), checked by the change
  rules of the official game (a faller only becomes a floater, a
  climber or a bomber; a bomber or a splashed pingu does not change);
- the timings of the actions follow the clocks of the official game:
  the digger digs every 4th tick, the miner every 4, the basher by its
  frame, the bridger in steps of 14, 16 and 9 ticks, the waiter 82
  ticks, the splashed 16, the bomber dies at the end of its animation;
- the ice melts while a pingu was on it in the last 1000 ticks, the
  spike keeps its own clock, and a teleporter checks every tick.

A danger (water, out of the screen) no longer aborts an action from
outside: as the official game, the actions check the water themselves,
and only leaving the screen kills a pingu at any time.
