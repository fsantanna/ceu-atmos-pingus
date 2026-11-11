#!/bin/sh
# Runs all the tests, with no screen.
#
#   tst/run.sh          runs and compares with the stored outputs
#   tst/run.sh update   stores the new outputs as the expected ones
#
#   - the data: every converted file loads with X.load;
#   - the engine: a sprite, a text, and a scripted click;
#   - the screens: screenshots at fixed frames, compared with tst/shots/;
#   - the levels: the scripted levels of tst/levels.txt, whose traces are
#     compared with tst/golden/.

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
OUT=$ROOT/out
mkdir -p "$OUT" tst/golden tst/shots
FAIL=0
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PINGUS_MUTE=1

check () {     # name, file
    if [ "$UPDATE" = 1 ]; then
        cp "$2" "tst/golden/$1.out"
    elif cmp -s "$2" "tst/golden/$1.out"; then
        echo "ok      $1"
    else
        echo "FAIL    $1"; FAIL=1
        diff "tst/golden/$1.out" "$2" | head -10
    fi
}

[ "$1" = "update" ] && UPDATE=1

# one build of the game for all the tests
./run.sh -o "$OUT/pingus" main.atm || exit 1
export PINGUS_BIN="$OUT/pingus"

# data
find data -name '*.atm' | sort > "$OUT/files.txt"
./run.sh tools/check.atm "$OUT/files.txt" | sed 's/slowest.*//' > "$OUT/data.out" 2>&1
check data "$OUT/data.out"

# engine
PINGUS_FRAMES=40:25 PINGUS_MOUSE="15:mv:400:300,20:dn:400:300:1,21:up:400:300:1" \
    ./run.sh tst/engine.atm > "$OUT/engine.out" 2>&1
check engine "$OUT/engine.out"

# screens: the menu, the levelsets, a level started
HD=$(mktemp -d)
PINGUS_HOME=$HD PINGUS_FRAMES=150:25 \
PINGUS_MOUSE="60:dn:275:350:1,61:up:275:350:1,100:mv:300:250,110:dn:300:250:1,111:up:300:250:1" \
PINGUS_SHOT="50:$OUT/menu.png,90:$OUT/levelsets.png,140:$OUT/start.png" \
    "$PINGUS_BIN" > "$OUT/screens.out" 2>&1
PINGUS_HOME=$HD PINGUS_FRAMES=300:25 PINGUS_KEYS="2:dn:Return" PINGUS_SHOT="290:$OUT/game.png" \
    "$PINGUS_BIN" data/levels/tutorial/snow7-grumbel.pingus.atm >> "$OUT/screens.out" 2>&1
rm -rf "$HD"
for s in menu levelsets start game; do
    if [ "$UPDATE" = 1 ]; then
        cp "$OUT/$s.png" "tst/shots/$s.png"
    elif cmp -s "$OUT/$s.png" "tst/shots/$s.png"; then
        echo "ok      shot $s"
    else
        echo "FAIL    shot $s ($OUT/$s.png)"; FAIL=1
    fi
done
check screens "$OUT/screens.out"

# levels, 4 at a time
grep -v '^#' tst/levels.txt | grep -v '^\s*$' | \
while read name frames level orders keys; do
    [ "$orders" = "-" ] && orders=""
    [ "$keys" = "-" ] && keys=""
    echo "tst/play.sh data/levels/$level.pingus.atm $frames '$orders' '$keys' > $OUT/$name.out 2>&1"
done | xargs -P 4 -I{} sh -c {}
for name in $(grep -v '^#' tst/levels.txt | grep -v '^\s*$' | awk '{print $1}'); do
    check "$name" "$OUT/$name.out"
done

[ "$UPDATE" = 1 ] && echo "updated" && exit 0
[ $FAIL = 0 ] && echo "all tests passed" || echo "SOME TESTS FAILED"
exit $FAIL
