#!/usr/bin/env python3
import sys
import math
import itertools
import numpy

DEBUG = False
DEBUG_WALK = False

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

# debug print - iterator has to be copied, otherwise it is consumed
if DEBUG:
    print('n=%d size=%d last=%d last_prev=%d min_dist=%d max_dist=%d distblock=%s' % (n, size, last, last_prev, min_dist, max_dist, str(list(itertools.tee(distblock)))))

# part 1 - smart approach
# the input is contained on the external ring of the spiral
# run through the items and cycle the distblock until we hit n
for c, dist in zip(range(last, last_prev, -1), itertools.cycle(distblock)):
    if (c == n):
        print(c, dist)
        break

# part 2 - brute force approach
# walk the spirals and keep updating the sums as we go
sums = numpy.zeros([size, size], int)
x, y = int(size/2), int(size/2)
sums[x][y] = 1
i = 1
for ring_size in range(3, size+1, 2):
    # calculate steps for current spiral
    steps = [( 0,  1)] +\
            [(-1,  0)] * (ring_size-2) +\
            [( 0, -1)] * (ring_size-1) +\
            [( 1,  0)] * (ring_size-1) +\
            [( 0,  1)] * (ring_size-2) +\
            [( 0,  1)]
    if DEBUG:
        print('steps for ring_size=%d: %s' % (ring_size, steps))

    # walk the steps on the current ring and update sums
    for st in steps:
        x += st[0]
        y += st[1]
        i += 1

        # only check we're walking the array properly
        if DEBUG_WALK:
            sums[x][y] = i
            print(x,y)
            print(sums)
            continue

        # sum the items in the neighborhood of the current cell
        in_range = lambda n: n[0]>=0 and n[0]<size and n[1]>=0 and n[1]<size
        neighbors = itertools.product((-1, 0, 1), (-1, 0, 1))
        neighbors_coords = filter(in_range, map(lambda n: (x+n[0], y+n[1]), neighbors))
        sums[x][y] = sum([sums[nx][ny] for nx, ny in neighbors_coords])

        if DEBUG:
            print(sums)
            print('')

        # print the desired value
        if sums[x][y] > n:
            print(n, sums[x][y])
            break

    if sums[x][y] > n:
        break

# vim:sts=4:sw=4:et:
