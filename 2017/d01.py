#!/usr/bin/env python3
import sys
from pathlib import Path as _P

INPUT_DEFAULT = _P(__file__).with_name('%s-input.txt' % _P(__file__).stem)
INPUT = sys.argv[1] if len(sys.argv) > 1 else INPUT_DEFAULT

with open(INPUT) as f:
    s = ''.join(map(str.strip, f.readlines()))
l = len(s)

total1 = sum([int(c) if c == s[i+1] else 0 for i, c in enumerate(s[:-1])])
total1 += int(s[-1]) if s[0] == s[-1] else 0
total2 = sum([int(c) if c == s[(i+int(l/2))%l] else 0 for i, c in enumerate(s[:-1])])

print(total1, total2)

# vim:sts=4:sw=4:et:
