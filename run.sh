#!/bin/sh
# Builds and runs a program of the game with the Atmos compiler.
#
#   ./run.sh [file.atm] [args]      (default: main.atm)
#
# Environment:
#   ATMOS     the compiler (default: ../lang/atmos, a checkout of
#             ia-atmos/lang next to this one, or `atmos`)
#   ATMOS_ASAN=1 builds with the address sanitizer

ROOT=$(cd "$(dirname "$0")" && pwd)

if [ -z "$ATMOS" ]; then
    ATMOS=atmos
    # the checkout of ia-atmos/lang, by its name or by its former names
    for d in lang ia-atmos/lang ceu-atmos fsantanna/ceu-atmos; do
        if [ -x "$ROOT/../$d/atmos" ]; then
            ATMOS="$ROOT/../$d/atmos"
            break
        fi
    done
fi

FILE=${1:-main.atm}
[ $# -gt 0 ] && shift

export ATMOS_CFLAGS="${ATMOS_CFLAGS:--O2} -I$ROOT"
export ATMOS_LDFLAGS="-lSDL2 -lSDL2_image -lSDL2_mixer -lm"

cd "$ROOT" && exec "$ATMOS" "$FILE" "$@"
