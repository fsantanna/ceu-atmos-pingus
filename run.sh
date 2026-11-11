#!/bin/sh
# Builds and runs a program of the game with the Atmos compiler.
#
#   ./run.sh [file.atm] [args]      (default: main.atm)
#
# Environment:
#   ATMOS     the compiler (default: ../ceu-atmos/atmos, or `atmos`)
#   ATMOS_ASAN=1 builds with the address sanitizer

ROOT=$(cd "$(dirname "$0")" && pwd)

if [ -z "$ATMOS" ]; then
    if [ -x "$ROOT/../ceu-atmos/atmos" ]; then
        ATMOS="$ROOT/../ceu-atmos/atmos"
    elif [ -x "$ROOT/../fsantanna/ceu-atmos/atmos" ]; then
        ATMOS="$ROOT/../fsantanna/ceu-atmos/atmos"
    else
        ATMOS=atmos
    fi
fi

FILE=${1:-main.atm}
[ $# -gt 0 ] && shift

export ATMOS_CFLAGS="${ATMOS_CFLAGS:--O2} -I$ROOT"
export ATMOS_LDFLAGS="-lSDL2 -lSDL2_image -lSDL2_mixer -lm"

cd "$ROOT" && exec "$ATMOS" "$FILE" "$@"
