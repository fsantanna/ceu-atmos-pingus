#!/bin/sh
# The game played with the mouse only, on tutorial/snow7 (view at 0,440):
# selects the bomber button, clicks on the first pingu, pauses and
# resumes with the button, holds fast forward, and double clicks the
# armageddon button.
ROOT=$(cd "$(dirname "$0")/.." && pwd)
HD=$(mktemp -d)
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PINGUS_MUTE=1 PINGUS_HOME="$HD" \
PINGUS_TRACE=1 PINGUS_FRAMES="900:25" PINGUS_KEYS="2:dn:Return" \
PINGUS_MOUSE="20:dn:30:260:1,21:up:30:260:1,\
170:dn:347:330:1,171:up:347:330:1,\
200:dn:705:565:1,201:up:705:565:1,260:dn:705:565:1,261:up:705:565:1,\
300:dn:745:565:1,400:up:745:565:1,\
500:dn:775:565:1,501:up:775:565:1,520:dn:775:565:1,521:up:775:565:1" \
    ${PINGUS_BIN:-"$ROOT/run.sh" main.atm} data/levels/tutorial/snow7-grumbel.pingus.atm
rm -rf "$HD"
