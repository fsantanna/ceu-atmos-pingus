#!/bin/sh
# The options: clicks on the screen of options change them and save
# them (an old save with `sound` and `music` as booleans gets volumes),
# and the scrolling options change the view of a level: autoscroll only
# with the mouse grabbed, drag and drop or the band with the right
# button. Screenshots of the options screen and of the menu with the
# cursor of the game and the frames per second.
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=${OUT:-$ROOT/out/tst}
BIN=${PINGUS_BIN:-"$ROOT/run.sh main.atm"}
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PINGUS_MUTE=1
mkdir -p "$OUT"

# the screen: Print FPS, the next language, master volume off, the
# software cursor, then Escape
HD=$(mktemp -d)
echo '[options=[sound=true, music=false], levels=[]]' > "$HD/.pingus-atmos.atm"
PINGUS_HOME=$HD PINGUS_FRAMES=80:25 PINGUS_KEYS=10:dn:F5,60:dn:Escape \
PINGUS_MOUSE="15:dn:90:370:1,16:up:90:370:1,20:dn:700:250:1,21:up:700:250:1,25:dn:700:330:1,26:mv:545:330,27:up:545:330:1,30:dn:90:255:1,31:up:90:255:1,35:mv:300:450" \
PINGUS_SHOT="50:$OUT/options.png,75:$OUT/overlay.png" $BIN
cat "$HD/.pingus-atmos.atm"
rm -rf "$HD"

# the scrolling, in a level: whether the view moved
L=data/levels/tutorial/snow7-grumbel.pingus.atm
view () {      # name, options, mouse
    HD=$(mktemp -d)
    echo "[options=[$2], levels=[]]" > "$HD/.pingus-atmos.atm"
    PINGUS_HOME=$HD PINGUS_FRAMES=90:25 PINGUS_KEYS=2:dn:Return PINGUS_MOUSE="$3" \
    PINGUS_SHOT="85:$OUT/view-$1.png" $BIN $L > /dev/null 2>&1
    rm -rf "$HD"
}
view base     "grab=false"                    "20:mv:400:300"
view auto     "grab=true"                     "20:mv:795:300"
view noauto   "grab=true, autoscroll=false"   "20:mv:795:300"
view nograb   "grab=false"                    "20:mv:795:300"
view drag     "dragdrop=true"                 "20:dn:400:300:3,30:mv:200:300,40:mv:100:300"
view band     "dragdrop=false"                "20:dn:400:300:3,30:mv:200:300,40:mv:100:300"
for v in auto noauto nograb drag band; do
    if cmp -s "$OUT/view-base.png" "$OUT/view-$v.png"; then
        echo "$v: still"
    else
        echo "$v: scrolled"
    fi
done
cmp -s "$OUT/view-drag.png" "$OUT/view-band.png" && echo "drag = band" || echo "drag != band"
