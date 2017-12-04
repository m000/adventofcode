#!/usr/bin/env python3
import sys
from pathlib import Path as _P

INPUT_DEFAULT = _P(__file__).with_name('%s-input.txt' % _P(__file__).stem)
INPUT = sys.argv[1] if len(sys.argv) > 1 else INPUT_DEFAULT

nvalid1 = 0
nvalid2 = 0

with open(INPUT) as f:
    for l in f:
        words1 = l.split()
        words1_uniq = set(words1)
        if len(words1) == len(words1_uniq):
            nvalid1 += 1

        words2 = list(map(lambda s: ''.join(s), map(sorted, l.split())))
        words2_uniq = set(words2)
        if len(words2) == len(words2_uniq):
            nvalid2 += 1

print(nvalid1, nvalid2)

# vim:sts=4:sw=4:et:
