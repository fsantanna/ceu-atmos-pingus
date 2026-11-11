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

## The port and the official game

Both measured in the same container, one after the other: the port
(`out/pingus`, from `tst/run.sh`) and the official game,
`Pingus/pingus` at `ffe3851`, built as in `tools/bench/README.md`
(release build, its default `sdl` renderer, window of 800x600, run
with `-s -m --no-cfg-file -w`). Its frame cap is 40 fps, as the port;
`--fps 100000` lifts it. 10 s each.

| Scenario | Port memory | Official memory | Port CPU | Official CPU | Port frames | Official frames |
|----------|-------------|-----------------|----------|--------------|-------------|-----------------|
| Start menu, idle | 41.3 MB | 39.5 MB | 0.97 s | 1.09 s | 396 | 394 |
| Tutorial level (snow7), no input | 37.5 MB | 34.9 MB | 0.88 s | 1.02 s | 397 | 395 |
| Same level, no frame cap | 37.4 MB | 35.0 MB | 9.95 s | 10.01 s | 6850 | 8472 |
| 100 pingus (crowdus013), no input | 37.3 MB | 34.8 MB | 0.92 s | 0.91 s | 397 | 395 |
| Same, no frame cap | 37.3 MB | 34.8 MB | 9.91 s | 10.00 s | 6999 | 8957 |

| | Port | Official |
|-|------|----------|
| Binary, stripped | 1.5 MB | 3.0 MB |

Measured earlier with the port alone (keys are scripted only in the
port, `PINGUS_KEYS`):

| Scenario | Peak memory | CPU in 10 s | Frames in 10 s |
|----------|-------------|-------------|----------------|
| 100 pingus, fast forward | 56.8 MB | 1.98 s | 396 |
| Same, fast forward, no frame cap | 57.0 MB | 9.94 s | 4958 |
| 100 pingus, armageddon at 5 s | 62.0 MB | 2.70 s | 395 |

| | |
|-|-|
| Time to the first frame (menu) | 93 ms |
| Time to the first frame of the largest level (crowdus007Asdc, 334 KB) | 141 to 178 ms |
| `X.load` of the largest level | 2 ms (`tools/check.atm`) |
| Build, from the sources | 24 s (the C compiler, `-O2`, one C file) |

## Reading

- Memory: the port uses 1.05x the memory of the official game in the
  menu and 1.07x in a level. The level keeps the ground map as one
  surface of the size of the level, plus its tiles as textures, and the
  collision map.
- CPU at 40 fps: the same as the official game (0.9x to 1.0x); most of
  it is the software renderer of SDL.
- Uncapped, the official game draws 1.2x to 1.3x the frames of the
  port (8472 against 6850 in the tutorial level): the cost of a frame
  of the port is 1.46 ms, of the official game 1.18 ms. The difference
  is a fixed cost per frame, not a cost per pingu: with 100 pingus,
  both games draw as many frames as with a few (6999 and 8957).
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
