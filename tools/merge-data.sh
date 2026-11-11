#!/bin/sh
# The source of the data of the port: the data of the 2018 fork, for the
# images and their sprite descriptions (the sprites of the port follow
# them), with the data of the official game on top for the levels,
# levelsets, worldmaps, prefabs, stories, demos, and the images that
# the 2018 fork does not have.
#
#   tools/merge-data.sh <data of fsantanna/pingus@036852a> <data of Pingus/pingus@ffe3851> <out>
#
# Then: tools/convert.py <out> data
set -e
OLD=$1; NEW=$2; OUT=$3
rm -rf "$OUT"
cp -r "$OLD" "$OUT"
for d in levels levelsets worldmaps prefabs stories; do
    rm -rf "$OUT/$d"
    cp -r "$NEW/$d" "$OUT/$d"
done
# new images, never replacing the old ones
(cd "$NEW/images" && find . -type f) | while read f; do
    [ -e "$OUT/images/$f" ] || { mkdir -p "$(dirname "$OUT/images/$f")"; cp "$NEW/images/$f" "$OUT/images/$f"; }
done
