#!/usr/bin/env python3
import sys
import re
import numpy
from pprint import pprint
from multiprocessing import Pool

INPUT = 'd11-input.txt'
GRIDW = 300
GRIDH = 300
DEBUG = False

# The current implementation runs reasonably fast. The key factor that
# makes it speedy enough is the use of numpy.ndarray.sum() instead of a
# python construct. Additionally, we use the multiprocessing module to
# calculate the best square for many different dimensions in parallel.
#
# There is still some room for optimization. Let's call sq(n) the values
# of squares with dimension n. We can calculate sq(n) incrementally, if
# sq(n-1) has already been calculated. However, after this optimization
# using the multiprocessing module will be much more complex.
#
# Note: We use x, y to refer to grid coords (base-1).
#       We use j, i to refer to array indices (base-0).
#

# ------------------------------------------------
# Helpers doing the work
# ------------------------------------------------
def calculate_cell_power(coords, gridno):
    x, y = coords
    rackid = x + 10
    power = rackid * y
    power += gridno
    power *= rackid
    power = (power // 100) % 10
    power -= 5
    return power

def calculate_square_power(coords, gridno, sqdim):
    x, y = coords
    i, j = y-1, x-1
    return cell_power[i:i+sqdim, j:j+sqdim].sum()

def best_square(sqdim):
    max_power = 0
    max_coords = None
    for y in range(1, GRIDH+1):
        if y + sqdim - 1 > GRIDH: continue
        for x in range(1, GRIDW+1):
            if x + sqdim - 1 > GRIDW: continue
            power = calculate_square_power((x,y), gridno, sqdim)
            if power > max_power:
                max_power = power
                max_coords = (x, y)
    return (sqdim, max_coords, max_power)

# ------------------------------------------------
# Read input and initialize cell cache
# ------------------------------------------------
with open(INPUT) as f:
    gridno = int(f.readline())

cell_power = numpy.zeros((GRIDW, GRIDH), dtype=numpy.int8)
for i in numpy.arange(GRIDH):
    for j in numpy.arange(GRIDW):
        # cache indexes are base-0, grid indexes are base-1
        x, y = j+1, i+1
        cell_power[i, j] = calculate_cell_power((x, y), gridno)

# ------------------------------------------------
# part 1
# ------------------------------------------------
sqdim = 3
print(best_square(sqdim))

# ------------------------------------------------
# part 2
# ------------------------------------------------
pool = Pool()
dims = list(range(1, min(GRIDW, GRIDH)+1))
r = pool.map_async(best_square, dims)
best = max(r.get(), key=lambda t: t[2])
print(best)

# vim:sts=4:sw=4:et:
