#!/bin/sh
# Compares all the demos (tools/compare.sh), and counts them.
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
mkdir -p out/compare
find data/levels -name '*.pingus-demo.atm' | sort | \
    xargs -P ${1:-4} -I{} sh -c 'tools/compare.sh {} > out/compare/$(basename {} .pingus-demo.atm).res 2>&1'
cat out/compare/*.res | grep -v '^[<>-]\|^[0-9]' > out/compare.txt
echo "same:    $(grep -c '^same' out/compare.txt)"
echo "differ:  $(grep -c '^differ' out/compare.txt)"
echo "none:    $(grep -c '^none' out/compare.txt)"
