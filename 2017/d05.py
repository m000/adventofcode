#!/usr/bin/env python3
import sys
from pathlib import Path as _P

INPUT_DEFAULT = _P(__file__).with_name('%s-input.txt' % _P(__file__).stem)
INPUT = sys.argv[1] if len(sys.argv) > 1 else INPUT_DEFAULT

# part 1
i = 0
steps = 0
with open(INPUT) as f:
    j = [int(l) for l in f]
while i < len(j) and i >= 0:
    j[i] += 1
    i += j[i]-1
    steps += 1
print(steps)

# part 2
i = 0
steps = 0
with open(INPUT) as f:
    j = [int(l) for l in f]
while i < len(j) and i >= 0:
    d = 1 if j[i] < 3 else -1
    j[i] += d
    i += j[i]-d
    steps += 1
print(steps)

# vim:sts=4:sw=4:et:
