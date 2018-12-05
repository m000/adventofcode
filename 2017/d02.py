#!/usr/bin/env python3
import sys
from pathlib import Path as _P

INPUT_DEFAULT = _P(__file__).with_name('%s-input.txt' % _P(__file__).stem)
INPUT = sys.argv[1] if len(sys.argv) > 1 else INPUT_DEFAULT

checksum1 = 0
checksum2 = 0

with open(INPUT) as f:
    for l in f:
        cells = list(map(int, l.split()))

        checksum1 += max(cells) - min(cells)

        assert len(cells) == len(set(cells)), 'Line with duplicate in input.'
        for c1 in cells:
            for c2 in cells:
                if (c1 != c2 and c1 % c2 == 0):
                    checksum2 += int(c1/c2)

print(checksum1, checksum2)

# vim:sts=4:sw=4:et:
