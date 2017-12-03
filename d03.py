#!/usr/bin/env python3
import sys
import math
import itertools

n = int(sys.argv[1]) if len(sys.argv) > 1 else 325489

# the size of the spiral side required to include the input - size must be odd number
size = int(math.sqrt(n))
size += 1 if size**2 < n else 0
size += 1 if size % 2 == 0 else 0

# the last cells in the two external spirals - size must be odd number for both
last = size**2
last_prev = (size-2)**2

# minimum/maximum distances from the center
min_dist = int(size/2)
max_dist = 2*int(size/2)

# in the external ring, distances take values between max_dist to min_dist
# the following block of distances is cycled over
# e.g. for size=5, this would be [4, 3, 2, 3]
distblock = itertools.chain(range(max_dist, min_dist-1, -1), range(min_dist+1, max_dist, 1))

# debug print - consumes distblock if enabled!
#print('n=%d size=%d last=%d last_prev=%d min_dist=%d max_dist=%d distblock=%s' % (n, size, last, last_prev, min_dist, max_dist, str(list(distblock))))

# the input is contained on the external ring of the spiral
# run through the items and cycle the distblock until we hit n
for c, dist in zip(range(last, last_prev, -1), itertools.cycle(distblock)):
    if (c == n):
        print(c, dist)
        break

# vim:sts=4:sw=4:et:
