#!/bin/sh
# The demos of the official game name levels by paths that its data no
# longer has (xskat/ok/..., moved since). Links each missing level to the
# file of the same name, so that the official game plays its own demos.
#
#   tools/bench/link-levels.sh path/to/official
cd "$1/data" || exit 1
find levels -name '*.pingus-demo' | while read d; do
    l=$(grep -o 'name "[^"]*"' "$d" | head -1 | sed 's/name "//;s/"//')
    [ -f "levels/$l.pingus" ] && continue
    f=$(find levels -iname "$(basename "$l").pingus" | head -1)
    [ -n "$f" ] || continue
    mkdir -p "$(dirname "levels/$l")"
    ln -sf "$(realpath "$f")" "levels/$l.pingus"
done
