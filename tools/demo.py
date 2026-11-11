#!/usr/bin/env python3

# Converts a demo of the original game (a converted `.pingus-demo.atm`)
# into the orders of the test mode of the port (PINGUS_ORDERS), and
# prints the level and the orders:
#
#   tools/demo.py DEMO
#   ->  data/levels/LEVEL.pingus.atm  time:id:action,...
#
# The time of a demo is in ticks of the world, and the id of a pingu is
# its order of release, as in the port. One recording drives both games.

import os
import re
import sys

# A level by its name, or by its file name in any directory, in any
# case, as some demos name it.
def find (name):
    path = 'data/levels/%s.pingus.atm' % name
    if os.path.exists(path):
        return path
    base = os.path.basename(name).lower() + '.pingus.atm'
    for d, _, fs in os.walk('data/levels'):
        for f in fs:
            if f.lower() == base:
                return os.path.join(d, f)
    return path

src = open(sys.argv[1], encoding='utf-8').read()
level = re.search(r':level \[name = "([^"]+)"\]', src).group(1)
orders = re.findall(r':pingu_action \[time = (\d+), id = (\d+), action = :(\w+)\]', src)
print(find(level),
      ','.join('%s:%s:%s' % o for o in orders))
