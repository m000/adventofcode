#!/usr/bin/env python3
import sys
import os
import json
import numpy
from scipy.spatial import distance
from multiprocessing import Pool
from pprint import pprint

INPUT = 'd06-input.txt'
CACHE_DIR = 'd06_cache'

# ------------------------------------------------
# read coords
# ------------------------------------------------
coords = []
with open(INPUT) as f:
    for ln, line in enumerate(f):
        line = line.strip()
        coords.append(tuple(map(int, line.split(','))))
coords.sort()
maxX = max([x for x, y in coords])  # rows
maxY = max([y for x, y in coords])  # cols


# ------------------------------------------------
# helpers for loading data
# ------------------------------------------------
def process_row(input_data):
    ''' Computes or loads one grid row.
    '''
    i, maxY, coords = input_data
    jf = os.path.join(CACHE_DIR, '%03d_cache.json' % (i))

    if os.path.isfile(jf):
        return jf

    output_data = []
    for j in range(maxY):
        dist = [distance.cityblock((i, j), p) for p in coords]
        dist_nearest = min(dist)
        dist_total = sum(dist)
        nearest = [pi for pi, d in enumerate(dist) if d == dist_nearest]
        nearest = nearest[0] if len(nearest) == 1 else -1
        output_data.append((nearest, int(dist_nearest), int(dist_total)))

    print(jf, file=sys.stderr)
    with open(jf, 'w') as f:
        json.dump([i, tuple(zip(*output_data))], f, indent=2)
    return jf

def load_grid(cache_files):
    ''' Loads all distance/nearest point rows in numpy arrays.
    '''
    for jf in sorted(cache_files):
        with open(jf, 'r') as f:
            i, (n, nd, td) = json.load(f)
        grid_n[i:i+1] = n
        grid_nd[i:i+1] = nd
        grid_td[i:i+1] = td


# ------------------------------------------------
# load distance/nearest point arrays
# ------------------------------------------------
grid_n = numpy.empty((maxX, maxY), dtype=numpy.int32)   # nearest index
grid_nd = numpy.empty((maxX, maxY), dtype=numpy.int32)  # nearest distance
grid_td = numpy.empty((maxX, maxY), dtype=numpy.int32)  # total distance
os.makedirs(CACHE_DIR, exist_ok=True)
pool = Pool()
input_data = [(i, maxY, coords) for i in range(maxX)]
r = pool.map_async(process_row, input_data, callback=load_grid)
r.wait()
print('grid data loaded', file=sys.stderr)


# ------------------------------------------------
# identify coords with infinite areas
# ------------------------------------------------
coords_infinite = [False,] * len(coords)
for pi in grid_n[0]:
    if pi == -1: continue
    coords_infinite[pi] = True
for pi in grid_n[-1]:
    if pi == -1: continue
    coords_infinite[pi] = True
for pi in grid_n[:,0]:
    if pi == -1: continue
    coords_infinite[pi] = True
for pi in grid_n[:,-1]:
    if pi == -1: continue
    coords_infinite[pi] = True


# ------------------------------------------------
# part 1
# ------------------------------------------------
coords_areas = [
    -1 if coords_infinite[pi] else numpy.count_nonzero(grid_n == pi)
    for pi, p in enumerate(coords)
]
print(max(coords_areas))

# ------------------------------------------------
# part 2
# ------------------------------------------------
print(numpy.count_nonzero(grid_td < 10000))

# vim:sts=4:sw=4:et:
