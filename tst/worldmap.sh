#!/bin/sh
# The worldmap with the first level solved: the second dot is open, a
# click on it walks the pingu there, and the position is saved.
ROOT=$(cd "$(dirname "$0")/.." && pwd)
HD=$(mktemp -d)
echo '[levels=[@"data/levels/tutorial/digger-tutorial2-grumbel.pingus.atm"=[solved=true, saved=6]], stories=[@"stories/tutorial_intro.story"=true]]' > "$HD/.pingus-atmos.atm"
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PINGUS_MUTE=1 PINGUS_HOME="$HD" \
PINGUS_FRAMES="200:25" PINGUS_MOUSE="20:dn:505:290:1,21:up:505:290:1" \
    ${PINGUS_BIN:-"$ROOT/run.sh" main.atm} data/worldmaps/tutorial.worldmap.atm
cat "$HD/.pingus-atmos.atm"
rm -rf "$HD"
