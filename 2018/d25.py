#!/usr/bin/env python3
import sys
import itertools
import numpy as np
from scipy.spatial import distance
from scipy.sparse import csr_matrix
from scipy.sparse import csgraph
from pprint import pprint

INPUTS = ['d25-input.txt', 'd25-input-example1.txt']
DEBUG = False
INPUT = INPUTS[1] if DEBUG else INPUTS[0]

# ------------------------------------------------
# read and label coords
# ------------------------------------------------
coords = []
with open(INPUT) as f:
    for ln, line in enumerate(f):
        line = line.strip()
        coords.append(tuple(map(int, line.split(','))))
coords.sort()

# we need to label all coords, as even points not belonging
# to any cluster need to be counted
print("Labeling coords...", file=sys.stderr)
labels = {}; labels_reverse = {}
for n, p in enumerate(coords):
    labels[p] = n
    labels_reverse[n] = p

# ------------------------------------------------
# calculate distance matrix
# ------------------------------------------------
print("Creating %dx%d direct distance matrix..." % (len(coords), len(coords)), file=sys.stderr)
csr_row = []; csr_col = []; csr_d = []
for p0, p1 in itertools.combinations(coords, 2):
    (l0, l1) = (labels[p0], labels[p1])
    d = distance.cityblock(p0, p1)
    if d <= 3:
        csr_row.append(l0)
        csr_col.append(l1)
        csr_d.append(d)
ddm = csr_matrix((csr_d, (csr_row, csr_col)), shape=(len(coords), len(coords)))

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html
print("Calculating shortest distance matrix...", file=sys.stderr)
distance = csgraph.shortest_path(ddm, method='D',
        directed=False, unweighted=False, return_predecessors=False)
print("Done.", file=sys.stderr)

# ------------------------------------------------
# part 1
# ------------------------------------------------
constellations = []
for s in map(set, zip(*np.where(np.isfinite(distance)))):
    attached = False
    for c in constellations:
        if c.intersection(s):
            c.update(s)
            attached = True
            break
    if not attached:
        constellations.append(s)
if DEBUG:
    pprint(constellations)
print(len(constellations))

# vim:sts=4:sw=4:et:
