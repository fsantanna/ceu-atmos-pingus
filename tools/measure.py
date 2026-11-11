#!/usr/bin/env python3

# Runs a command for some seconds, and reports its peak memory and its
# CPU time.
#
#   tools/measure.py SECONDS COMMAND...
#
# Prints: peak memory (VmHWM, in MB), CPU time (user + system, in s),
# and the elapsed time. With PINGUS_COUNT=1, the game prints its number
# of frames at exit, which goes to the report too.

import os
import subprocess
import sys
import time

def peak (pid):
    try:
        with open("/proc/%d/status" % pid) as f:
            for l in f:
                if l.startswith("VmHWM:"):
                    return int(l.split()[1]) / 1024.0
    except OSError:
        pass
    return None

def main ():
    secs = float(sys.argv[1])
    cmd = sys.argv[2:]
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    mem = 0.0
    while p.poll() is None and time.time() - t0 < secs:
        m = peak(p.pid)
        if m:
            mem = max(mem, m)
        time.sleep(0.05)
    m = peak(p.pid)
    if m:
        mem = max(mem, m)
    if p.poll() is None:
        p.terminate()
    _, err = p.communicate()
    elapsed = time.time() - t0
    ru = os.wait4 if False else None
    usage = __import__("resource").getrusage(__import__("resource").RUSAGE_CHILDREN)
    cpu = usage.ru_utime + usage.ru_stime
    frames = ""
    for l in err.decode(errors="replace").splitlines():
        if l.startswith("frames:"):
            frames = l.split()[1]
    print("peak %.1f MB, cpu %.2f s, elapsed %.2f s%s" %
          (mem, cpu, elapsed, (", frames " + frames) if frames else ""))

if __name__ == "__main__":
    main()
