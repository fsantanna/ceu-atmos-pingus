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
pixel off at the time of a click misses the click. The demos were
recorded over years, with engines older than the 2018 fork, and the
port follows the Céu rewrite of that fork, with the timings of the
official game where they differ (above). The rest is to compare with
the official game running, which could not be built in the session of
the port (see bench.md): its trace of the same demo would show the
first tick where the two games differ.

The differences found by reading the official code, and fixed:

- an entrance releases a pingu when the time is *past* the last release
  plus the rate: one every `rate + 1` ticks;
- in a tick, the pingus move first, then the objects react (exits,
  traps), so the objects drawn behind the pingus use a second phase,
  `:tock`;
- a faller decides how it lands in the tick of the collision (the Céu
  rewrite waited one tick, as a workaround), and the velocities are
  clamped to the terminal velocity.
