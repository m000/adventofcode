#!/usr/bin/env python3
import numpy
from pprint import pprint
INPUT = 'd02-input.txt'

with open(INPUT) as f:
    lines = list(map(str.strip, f.readlines()))

# ------------------------------------------------

twos = 0
threes = 0

for l in lines:
    chars, counts = numpy.unique(list(l), return_counts=True)
    twos += (2 in counts)
    threes += (3 in counts)

print('%d * %d = %d' % (twos, threes, twos*threes))
print('------------------------------------------------')

# ------------------------------------------------

# Note that we need to wrap result in list() when
# calculating numlines. Otherwise the loop will stop
# when the first map is exhausted.
l2n = lambda l: list(map(ord, l))
numlines1 = list(map(l2n, lines))
numlines2 = list(map(l2n, lines))
diffs = []

for i1, l1 in enumerate(numlines1):
    for i2, l2 in enumerate(numlines2):
        if (not i1 < i2): continue;
        d = numpy.not_equal(l1, l2)
        s = numpy.sum(d)
        diffs.append((s, (i1, i2)))

s, (i1, i2) = min(diffs)
l1 = lines[i1]
l2 = lines[i2]
common = ''
diff = ''
for i in range(len(lines[i1])):
    if (l1[i] == l2[i]):
        common += l1[i]
        diff += ' '
    else:
        diff += '^'

print('%04d:%s\n%04d:%s\ndiff:%s\n' % (i1, l1, i2, l2, diff))
print(common)

# vim:sts=4:sw=4:et:
