# Benchmark

Measured in a container with no screen (Ubuntu 24.04, 4 cores, SDL2
2.30 with its software renderer, `SDL_VIDEODRIVER=dummy`), sound off,
with `tools/measure.py`:

```
./run.sh -o /tmp/pingus main.atm
env SDL_VIDEODRIVER=dummy PINGUS_MUTE=1 PINGUS_COUNT=1 [PINGUS_FPS=0] \
    [PINGUS_KEYS=...] tools/measure.py 10 /tmp/pingus [LEVEL]
```

The frame rate is capped at 40 frames per second, as the original,
unless `PINGUS_FPS=0`. A tick of the world is 20ms; fast forward runs 4
ticks per 20ms.

## The port

| Scenario | Peak memory | CPU in 10 s | Frames in 10 s |
|----------|-------------|-------------|----------------|
| Start menu, idle | 41.2 MB | 1.05 s | 396 |
| Tutorial level (snow7), no input | 52.7 MB | 1.01 s | 396 |
| Same level, no frame cap | 52.6 MB | 9.99 s | 6538 |
| 100 pingus (crowdus013), fast forward | 56.8 MB | 1.98 s | 396 |
| Same, fast forward, no frame cap | 57.0 MB | 9.94 s | 4958 |
| 100 pingus, armageddon at 5 s | 62.0 MB | 2.70 s | 395 |

| | |
|-|-|
| Time to the first frame (menu) | 93 ms |
| Time to the first frame of the largest level (crowdus007Asdc, 334 KB) | 141 to 178 ms |
| `X.load` of the largest level | 2 ms (`tools/check.atm`) |
| Binary, stripped | 1.4 MB |
| Build, from the sources | 24 s (the C compiler, `-O2`, one C file) |

## The baseline

The plan measures the port against the official game, `Pingus/pingus`
at `ffe3851`. Its numbers, from the plan (the same kind of container,
software renderer, 10 s each):

| Program | Scenario | Peak memory | CPU in 10 s |
|---------|----------|-------------|-------------|
| official Pingus | start menu | 40.1 MB | 0.77 s |
| official Pingus | tutorial level, no input | 35.0 MB | 0.80 s |
| official Pingus | same level, no frame cap | 35.2 MB | 9.87 s |
| official Pingus | binary, stripped | 3.0 MB | |

The official game could not be built again in the session of the port:
installing its dependencies was not allowed there. The scenarios with
many pingus and the frame counts of the official game are still to be
measured, with the frame-count patch of the plan.

## Reading

- Memory: the port uses 1.0x the memory of the official game in the
  menu, and 1.5x in a level. The level keeps the ground map as one
  surface of the size of the level, plus its tiles as textures (a
  1920x1200 level is 9 MB for the surface alone), and the collision map.
- CPU at 40 fps: 1.3x the official game in both scenarios; most of it
  is the software renderer of SDL, as the uncapped runs show (the
  tutorial level draws 650 frames per second).
- With 100 pingus in fast forward (5 ticks per frame), the port still
  runs 500 frames per second uncapped: about 2 ms per frame for 100
  pingus, their sprites, and 5 ticks of the world.
- The tasks are cheap: a wake of a task costs about 55 ns in a micro
  benchmark (2000 tasks awaiting an event, 1000 events, 0.11 s).
- The first slow case found was the rain: 16 drops per tick, each one a
  task with a sprite. A bug made half of them never end (a sprite of
  one frame that did not loop waited forever), and the cost grew with
  the time. With the fix, a rainy level in fast forward takes 11 ms per
  frame, constant.
