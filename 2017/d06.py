#!/usr/bin/env python3
import sys
from pathlib import Path as _P

INPUT_DEFAULT = _P(__file__).with_name('%s-input.txt' % _P(__file__).stem)
INPUT = sys.argv[1] if len(sys.argv) > 1 else INPUT_DEFAULT

# part 1
i = 0
steps = 0
with open(INPUT) as f:
    b = [int(i) for i in f.read().split()]


b2s = lambda a: ' '.join(['%04d' % i for i in a])
seen = {}
n = 0
while True:
    s = b2s(b)
    if s in seen: break
    seen[s] = n
    n += 1

    idx, maxv = max(enumerate(b), key=lambda t: t[1])
    b[idx] = 0
    for i in range(maxv):
        idx = (idx+1) % len(b)
        b[idx] += 1

print(n, n-seen[s])

# vim:sts=4:sw=4:et:
