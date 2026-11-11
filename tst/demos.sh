#!/bin/sh
# Replays the demos of the original game (data/levels/**/demo/), the
# recorded solutions of the levels, in the port, and reports how many
# of them still solve their level: a measure of fidelity to the
# original. Slow (minutes): not part of tst/run.sh.
#
#   tst/demos.sh [JOBS]
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
OUT=$ROOT/out/demos
mkdir -p "$OUT"
[ -n "$PINGUS_BIN" ] || { ./run.sh -o out/pingus main.atm || exit 1; PINGUS_BIN=$ROOT/out/pingus; }
export PINGUS_BIN
for d in $(find data/levels -name '*.pingus-demo.atm' | sort); do
    set -- $(tools/demo.py "$d")
    grep -q "file = \"${1#data/}\",\s*$" data/levels.atm 2>/dev/null
    name=$(basename "$d" .pingus-demo.atm)
    [ -f "$1" ] || { echo "$name: no level" > "$OUT/$name.res"; continue; }
    echo "timeout 300 tst/play.sh $1 8000 '$2' '7900:dn:Escape,7950:dn:Escape' 2>&1 | grep -E '^saved' > $OUT/$name.out; \
          echo \"$name: \$(cat $OUT/$name.out)\" > $OUT/$name.res"
done | xargs -P ${1:-4} -I{} sh -c "{}"
cat "$OUT"/*.res | sort > "$OUT/../demos.txt"
echo "demos:   $(wc -l < "$OUT/../demos.txt")"
echo "solved:  $(grep -c ': solved' "$OUT/../demos.txt")"
echo "failed:  $(grep -c ': failed' "$OUT/../demos.txt")"
echo "other:   $(grep -vc ': solved\|: failed' "$OUT/../demos.txt")"
