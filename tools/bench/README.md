# The official game, for the benchmark and the comparisons

`official.patch` applies to `Pingus/pingus` at `ffe3851`. It adds:

- `PINGUS_TRACE=1`: the trace of the actions of the pingus, in the
  format of the port (time, pingu, action, x, y);
- `PINGUS_COUNT=1`: the number of frames drawn, printed at exit.

```
git clone https://github.com/Pingus/pingus official
git -C official checkout ffe3851
git -C official apply ../ceu-atmos-pingus/tools/bench/official.patch
apt-get install libsdl2-dev libsdl2-image-dev libsigc++-2.0-dev \
    libglm-dev libgl-dev libglu1-mesa-dev libpng-dev libopenal-dev \
    libvorbis-dev libogg-dev libmpg123-dev libopusfile-dev \
    libmodplug-dev libfmt-dev libgtest-dev libjsoncpp-dev libboost-dev
cmake -S official -B official/build -G Ninja -DCMAKE_BUILD_TYPE=Release
ninja -C official/build
```

Then `OFFICIAL=path/to/official tools/compare.sh DEMO` replays a demo in
both games and compares the traces.
