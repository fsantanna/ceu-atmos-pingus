#!/bin/sh
# Replays a demo of the original in the official game and in the port,
# and compares the traces of the actions of the pingus.
#
#   tools/compare.sh DEMO [FRAMES]
#
#   DEMO      data/levels/.../demo/NAME.pingus-demo.atm (of the port)
#
# OFFICIAL is a checkout of Pingus/pingus at ffe3851, built in build/,
# with tools/bench/official.patch applied (the trace of the port, and 100
# updates per frame in demos). Both traces are compared up to the tick
# 39000, which the port reaches in its 8000 frames. The
# first line of each pingu in the port, its creation as a faller, has
# no line in the official trace and is left out, and so are the lines
# of the port with no match there: abilities given (+climber) and
# orders refused.
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OFFICIAL=${OFFICIAL:-$ROOT/../src/official}
DEMO=$1
OUT=$ROOT/out/compare
mkdir -p "$OUT"
NAME=$(basename "$DEMO" .pingus-demo.atm)
ORIG=$(find "$OFFICIAL/data/levels" -name "$NAME.pingus-demo" | head -1)

UD=$(mktemp -d)
(cd "$OFFICIAL" && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PINGUS_TRACE=1 \
    PINGUS_DEMO_SPEED=100 timeout 60 ./build/pingus -d data -u "$UD" -s -m --no-cfg-file \
    -g 320x240 "$ORIG") 2>/dev/null | grep ' pingu ' | awk '$1 < 39000' > "$OUT/$NAME.official"
rm -rf "$UD"

set -- $("$ROOT/tools/demo.py" "$DEMO")
"$ROOT/tst/play.sh" "$1" "${FRAMES:-8000}" "$2" "7900:dn:Escape,7950:dn:Escape" 2>/dev/null \
    | grep ' pingu ' | grep -v ' +\| refuses:' | awk '$1 < 39000 { if (seen[$3]++) print }' > "$OUT/$NAME.port"

if [ ! -s "$OUT/$NAME.official" ]; then
    echo "none    $NAME (no trace of the official game)"
elif cmp -s "$OUT/$NAME.official" "$OUT/$NAME.port"; then
    echo "same    $NAME ($(wc -l < "$OUT/$NAME.port") lines)"
else
    echo "differ  $NAME"
    diff "$OUT/$NAME.official" "$OUT/$NAME.port" | head -${LINES_SHOWN:-6}
fi
