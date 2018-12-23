#!/usr/bin/env python3
import sys
import re
import itertools
import hashlib
import os
import numpy as np
import networkx as nx
from scipy.spatial import distance
from scipy.sparse import csr_matrix
from scipy.sparse import csgraph
from pprint import pprint

CACHE_DIR = 'd22_cache'
INPUTS = [ 'd22-input.txt', 'd22-input-example.txt']
DEBUG = False
INPUT = INPUTS[1] if DEBUG else INPUTS[0]

# switches between scipy and networkx for part 2
USENX = True

# ------------------------------------------------
# Class modeling the cave.
# ------------------------------------------------
class Cave:
    x0_factor = 48271
    y0_factor = 16807
    errosion_mod = 20183
    allowed_tools = {'.': 'TC', '=': 'CN', '|': 'TN'}

    def __init__(self, target, max_depth, max_width=None):
        self.target = (target[1], target[0])
        self.max_depth = max_depth
        self.max_width = max_width if max_width is not None else self.target[1]
        self.dims = (self.max_depth+1, self.max_width+1)
        self._tt = None

        # initialize caching
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.cachefile_base = os.path.join(CACHE_DIR, hashlib.md5(repr(self).encode('utf-8')).hexdigest())

        if self.cache_exists():
            print("Using cache for %s." % (repr(self)), file=sys.stderr)
            self.g = np.load(self.cache_g)
            self.e = np.load(self.cache_e)
            self.t = np.load(self.cache_t)
            return

        # initialize from scratch
        self.g = np.full(self.dims, -1, dtype=np.int32)
        self.e = np.full(self.dims, -1, dtype=np.int32)
        self.t = np.full(self.dims, '.', dtype=np.unicode)
        rx = range(self.dims[1]); ry = range(self.dims[0])
        for i, j in itertools.product(ry, rx):
            if (i, j) == self.target or (i, j) == (0, 0):
                self.g[i, j] = 0
            elif i == 0:
                self.g[i, j] = j * Cave.y0_factor
            elif j == 0:
                self.g[i, j] = i * Cave.x0_factor
            else:
                assert(self.e[i, j-1] != -1 and self.e[i-1, j] != -1)
                self.g[i, j] = self.e[i, j-1] * self.e[i-1, j]

            self.e[i, j] = (self.g[i, j] + self.max_depth) % Cave.errosion_mod
            m = self.e[i, j] % 3
            if m == 1:
                self.t[i, j] = '='
            elif m == 2:
                self.t[i, j] = '|'

        # write cache files
        with open(self.cache_info, 'w') as f:
            print(repr(self), file=f)
        np.save(self.cache_g, self.g)
        np.save(self.cache_e, self.e)
        np.save(self.cache_t, self.t)

    def cache_exists(self):
        return all(map(os.path.isfile, [self.cache_info, self.cache_g, self.cache_e, self.cache_t]))

    @property
    def cache_info(self): return '%s_info.txt' % self.cachefile_base

    @property
    def cache_g(self): return '%s_g.npy' % self.cachefile_base

    @property
    def cache_e(self): return '%s_e.npy' % self.cachefile_base

    @property
    def cache_t(self): return '%s_t.npy' % self.cachefile_base

    def risk(self, tl, br):
        a = self.t[tl[0]:br[0]+1, tl[1]:br[1]+1]
        return np.sum(a == '=') + 2*np.sum(a == '|')

    def tostring(self, tl, br):
        a = self.t[tl[0]:br[0]+1, tl[1]:br[1]+1]
        s = '\n'.join(np.apply_along_axis(lambda s: ''.join(s), axis=1, arr=a))
        return s

    def __repr__(self):
        return '<%s: x0f=%d y0f=%d em=%d d=%d w=%d t=%s>' % (self.__class__.__name__,
                self.__class__.x0_factor, self.__class__.y0_factor,
                self.__class__.errosion_mod, self.max_depth, self.max_width, self.target)

    def __str__(self):
        tl = (0, 0)
        br = self.dims
        return self.tostring(tl, br)

    def tools(self, i, j):
        if self.t[i, j] == '.':
            return ['T', 'C']
        elif self.t[i, j] == '=':
            return ['C', None]
        elif self.t[i, j] == '|':
            return ['T', None]
        else:
            assert(False)

    def update_paths(self, max_width=None, max_depth=None, indices=None):
        ''' Essentially we want to search the shortest path across a
            3 dimensional space. The first two dimensions are spatial.
            The third dimension represents the item currently held by
            the spelunker.
            This functions flattens the 3 dimensional space to a NxN
            array, and uses scipy.sparse.csgraph.shortest_path() to
            find the shortest paths between all points in the space.
            Using the indices argument of shortest_path() will limit
            the calculation to the points that are of interest.
        '''
        # Limit search space.
        assert(max_depth is None or max_depth < self.dims[0])
        assert(max_width is None or max_width < self.dims[1])
        max_depth = max_depth if max_depth is not None else self.dims[0]
        max_width = max_width if max_width is not None else self.dims[1]

        # Assign labels to vertices. Add distances for changing tools.
        print("Labelling cave...", file=sys.stderr)
        self.labels = {}; self.labels_reverse = {}
        csr_row = []; csr_col = []; csr_d = []
        nlabels = 0
        for i, j in itertools.product(range(max_depth), range(max_width)):
            tools = Cave.allowed_tools[self.t[i, j]]
            assert(len(tools) == 2)
            v0 = (i, j) + (tools[0],)
            l0 = nlabels
            self.labels[v0] = l0
            self.labels_reverse[l0] = v0
            nlabels += 1

            v1 = (i, j) + (tools[1],)
            l1 = nlabels
            self.labels[v1] = l1
            self.labels_reverse[l1] = v1
            nlabels += 1

            csr_row.append(l0); csr_col.append(l1); csr_d.append(7)

        # Create sparse direct distance matrix.
        print("Creating %dx%d direct distance matrix..." % (nlabels, nlabels), file=sys.stderr)
        for i, j in itertools.product(range(max_depth-1), range(max_width-1)):
            p0 = (i, j)
            type0 = self.t[i, j]
            tools0 = Cave.allowed_tools[type0]

            neighbors = ((0, 1), (0, -1), (1, 0), (-1, 0))
            for di, dj in neighbors:
                p1 = (p0[0] + di, p0[1] + dj)
                if not (p1[0] >=0 and p1[1] >=0): continue

                type1 = self.t[p1[0], p1[1]]
                tools1 = Cave.allowed_tools[type1]

                for t in set(tools0).intersection(set(tools1)):
                    v0 = p0 + (t,); l0 = self.labels[v0]
                    v1 = p1 + (t,); l1 = self.labels[v1]

                    csr_row.append(l0); csr_col.append(l1); csr_d.append(1)

        self.ddm = csr_matrix((csr_d, (csr_row, csr_col)), shape=(nlabels, nlabels), dtype=np.uint32)

        # Calculate shortest paths and set object path matrices.
        # If indices argument is None, distances for *all* pairs
        # will be calculated. This is *slow* and will require a
        # lot of memory.
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html
        print("Calculating shortest paths...", file=sys.stderr)
        if indices is not None:
            indices = [self.labels[p] for p in indices]
        self.distances = csgraph.shortest_path(self.ddm, method='D',
                directed=False, unweighted=False, return_predecessors=False, indices=indices)
        print("Done.", file=sys.stderr)

    def nxdist(self, start, end, max_width=None, max_depth=None):
        ''' SciPy's implementation of Dijkstra's algorithm operates
            on a numeric matrix. This means that the graph vertices
            have to be mapped to labels before running it.
            The implementation of Dijkstra's algorithm in networkx
            is a bit simpler, as there's no need to map vertices to
            labels.
        '''
        # Limit search space.
        assert(max_depth is None or max_depth < self.dims[0])
        assert(max_width is None or max_width < self.dims[1])
        max_depth = max_depth if max_depth is not None else self.dims[0]
        max_width = max_width if max_width is not None else self.dims[1]

        graph = nx.Graph()
        for i, j in itertools.product(range(max_depth-1), range(max_width-1)):
            p0 = (i, j)
            type0 = self.t[i, j]
            tools0 = Cave.allowed_tools[type0]
            assert(len(tools0) == 2)
            graph.add_edge((i, j, tools0[0]), (i, j, tools0[1]), weight=7)
            graph.add_edge((i, j, tools0[1]), (i, j, tools0[0]), weight=7)

            neighbors = ((0, 1), (0, -1), (1, 0), (-1, 0))
            for di, dj in neighbors:
                p1 = (p0[0] + di, p0[1] + dj)
                if p1[0] >=0 and p1[1] >=0:
                    type1 = self.t[p1[0], p1[1]]
                    tools1 = Cave.allowed_tools[type1]
                    for t in set(tools0).intersection(set(tools1)):
                        graph.add_edge(p0 + (t,), p1 + (t,), weight=1)
        return nx.dijkstra_path_length(graph, start, end)

# ------------------------------------------------
# load config
# ------------------------------------------------
with open(INPUT) as f:
    for l in f:
        if l.startswith('depth'):
            depth = int(l.split(':')[1])
        elif l.startswith('target'):
            target = tuple(map(int, l.split(':')[1].split(',')))

# ------------------------------------------------
# part 1
# ------------------------------------------------
c = Cave(target, depth)
print(repr(c))
print(c.risk((0, 0), c.target))

# ------------------------------------------------
# part 2
# ------------------------------------------------
c = Cave(target, max_depth=depth, max_width=target[0]+20)
print(repr(c))
print(c)
pstart = (0, 0, 'T')
pend = c.target + ('T',)
if USENX:
    print(c.nxdist(pstart, pend, max_depth=c.target[0]+20))
else:
    c.update_paths(max_depth=c.target[0]+20, indices=[pstart, pend])
    lstart, lend = (c.labels[pstart], c.labels[pend])
    print(c.distances[lstart, lend])

# vim:sts=4:sw=4:et:
