#!/usr/bin/env python3
import re
import sys
import numpy
from pprint import pprint
INPUT = 'd03-input.txt'

line_re = re.compile(r'#(?P<id>\d+) @ (?P<x>\d+),(?P<y>\d+): (?P<w>\d+)x(?P<h>\d+)')

# ------------------------------------------------

W = 0
H = 0
with open(INPUT) as f:
    for ln, line in enumerate(f):
        m = line_re.match(line.strip())
        if m is None:
            print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
            sys.exit(1)
        claim = {k: int(v) for k, v in m.groupdict().items()}
        W = max(W, claim['x'] + claim['w'])
        H = max(H, claim['y'] + claim['h'])
print('fabric size: %dx%d' % (W, H))

# ------------------------------------------------

# part 1
fabric = numpy.zeros((H, W), dtype=numpy.uint16)
with open(INPUT) as f:
    for ln, line in enumerate(f):
        m = line_re.match(line.strip())
        claim = {k: int(v) for k, v in m.groupdict().items()}
        fslice = fabric[claim['y']:claim['y']+claim['h'], claim['x']:claim['x']+claim['w']]
        patch = numpy.ones((claim['h'], claim['w']), dtype=numpy.uint16)
        fslice += patch
print('overlapping bits: %d' % len(fabric[fabric>1]))

# ------------------------------------------------

# part 2
with open(INPUT) as f:
    for ln, line in enumerate(f):
        m = line_re.match(line.strip())
        claim = {k: int(v) for k, v in m.groupdict().items()}
        fslice = fabric[claim['y']:claim['y']+claim['h'], claim['x']:claim['x']+claim['w']]
        patch = numpy.ones((claim['h'], claim['w']), dtype=numpy.uint16)
        if numpy.array_equal(fslice, patch):
            print('claim with no overlaps: %d' % claim['id'])

# vim:sts=4:sw=4:et:
