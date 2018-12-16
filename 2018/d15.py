#!/usr/bin/env python3
import re
import sys
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse import csgraph
from collections import Counter
from matplotlib import pyplot
from pprint import pprint
INPUTS = [ 'd15-input.txt', ]

DEBUG = True
INPUT = INPUTS[0] if DEBUG else INPUTS[0]

# ------------------------------------------------
# constants and global state
# ------------------------------------------------
units_max = 1000
units_re = r'([GE])'
units_hp = {'G': 200, 'E': 200}
units_ap = {'G': 3, 'E': 3}
units_id = {'G': iter(range(units_max)), 'E': iter(range(units_max))}

carts_turn = {
        '</':  'v', '>/':  '^', '^/':  '>', 'v/':  '<',
        '<\\': '^', '>\\': 'v', '^\\': '<', 'v\\': '>',
}
carts_iturn = {
        '<l': ('v', 's'), '>l': ('^', 's'), '^l': ('<', 's'), 'vl': ('>', 's'),
        '<s': ('<', 'r'), '>s': ('>', 'r'), '^s': ('^', 'r'), 'vs': ('v', 'r'),
        '<r': ('^', 'l'), '>r': ('v', 'l'), '^r': ('>', 'l'), 'vr': ('<', 'l'),
}

# ------------------------------------------------
# helpers
# ------------------------------------------------
class Unit:
    def __init__(self, upos, utype):
        self.posx, self.posy = upos
        self.type = utype
        self.hp = units_hp[self.type]
        self.ap = units_ap[self.type]
        self.id = next(units_id[self.type])

    def __str__(self):
        return '%s%d[hp=%d, ap=%d, pos=(%d, %d)]' % (
                self.type, self.id, self.hp, self.ap, self.posx, self.posy)

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return (self.posx, self.posy) < (other.posx, other.posy)

    @property
    def uid(self):
        return '%s%d' % (self.type, self.id)

    def move(self, board):
        ir = board.in_range(for_type=self.type)
        #print(ir)

class Board:
    def __init__(self, inputf):
        # read dimensions
        ldims = []
        with open(inputf) as f:
            for ln, line in enumerate(f):
                ldims.append( (ln, len(line.rstrip())) )
        self.dims = (max([d[0] for d in ldims])+1, max([d[1] for d in ldims]))

        # read data
        self.board = np.empty(self.dims, dtype=np.unicode)
        self.units = []
        with open(inputf) as f:
            for ln, line in enumerate(f):
                line = line.rstrip()
                if not line.lstrip(): continue
                self.board[ln] = list(line.ljust(self.dims[1]))
                for um in re.finditer(units_re, line):
                    upos, utype = (um.span()[0], ln), um.group(0)
                    u = Unit(upos, utype)
                    self.board[u.posy, u.posx] = '.'
                    self.units.append(u)
        self.units.sort()

        # initialize other state
        self.ts = 0
        self.inrange_cache = {'ts': -1}

    def __repr__(self):
        return '%s<%dx%d, %d units: %s>' % (self.__class__.__name__,
                self.dims[1], self.dims[0], len(self.units), self.units)

    def __str__(self):
        return self.tostring()

    def overlay(self, items, f = None):
        if f is not None:
            items = map(f, items)
        replaced = []
        for pos, o, valid in items:
            v = self.board[pos[0], pos[1]]
            assert(v == valid or valid is None)
            self.board[pos[0], pos[1]] = o
            replaced.append( (pos, v, o) )
        return replaced

    def tostring(self, overlay_units=True):
        if overlay_units:
            ubak = self.overlay(self.units, lambda u: ((u.posy, u.posx), u.type, '.'))
        s = '\n'.join(np.apply_along_axis(lambda s: ''.join(s), axis=1, arr=self.board))
        if overlay_units:
            self.overlay(ubak)
        return s

    def plot(self):
        # https://matplotlib.org/examples/color/colormaps_reference.html
        wcolor = 255    # wall
        scolor = 0      # space
        Ecolor = 66     # elf
        Gcolor = 110    # gnome
        rcolor = 220    # in range
        cprops = {
                'color': 'white',
                'fontweight': 'black',
                'fontfamily': 'monospace',
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
        }
        imdata = np.full(self.board.shape, wcolor, dtype=np.uint8)
        #----------------------
        coords = np.where(self.board == '.')
        imdata[coords] = scolor
        #----------------------
        inrange = self.in_range()
        coords = tuple(zip(*inrange.keys()))
        imdata[coords] = rcolor
        #----------------------
        coords = tuple(zip(*[(u.posy, u.posx) for u in self.units if u.type == 'G']))
        imdata[coords] = Gcolor
        #----------------------
        coords = tuple(zip(*[(u.posy, u.posx) for u in self.units if u.type == 'E']))
        imdata[coords] = Ecolor
        #----------------------
        img = pyplot.imshow(imdata, cmap='Paired')
        pyplot.show()

    def in_range(self, for_type=None):
        for_type = for_type if for_type is not None else 'all'
        if self.inrange_cache['ts'] == self.ts:
            return self.inrange_cache[for_type]

        self.inrange_cache = {'ts': self.ts, 'G': {}, 'E': {}, 'all': {}}
        for u in self.units:
            neighbors = [(u.posy+1, u.posx), (u.posy-1, u.posx), (u.posy, u.posx+1), (u.posy, u.posx-1)]
            for p in neighbors:
                if self.board[p[0], p[1]] != '.': continue
                for ft, cache in self.inrange_cache.items():
                    if ft == u.type: continue
                    if type(cache) != dict: continue
                    if p not in cache: cache[p] = []
                    cache[p].append(u.uid)
        return self.inrange_cache[for_type]

    def tick(self):
        # set unit locations as walls
        ubak = self.overlay(self.units, lambda u: ((u.posy, u.posx), '#', '.'))

        # We want scipy to compute shortest paths. For this, we need
        # to express the map as a NxN sparse matrix. The value at
        # (i, j) represents the direct distance between points labeled
        # i and j. 
        # For this, we need to extract the points we want, assign
        # them labels, create a sparse matrix and feed it to scipy.

        # make labels and sparse matrix indices
        coords_label = iter(range(self.dims[0] * self.dims[1]))
        coords = {}; labels = {}; csr_row = []; csr_col = []
        for i in np.arange(self.dims[0]-1):      # skip last row
            for j in np.arange(self.dims[1]-1):  # skip last column
                if self.board[i, j] != '.': continue

                # find neighbors
                # undirected graph - only need to check 2 neighbors
                neighbors = []
                if self.board[i, j+1] == '.':
                    neighbors.append((i, j+1))
                if self.board[i+1, j] == '.':
                    neighbors.append((i+1, j))
                if not neighbors: continue

                # set labels and distances
                p = (i, j)
                if p not in labels:
                    lp = next(coords_label)
                    labels[p] = lp
                    coords[lp] = p
                else:
                    lp = labels[p]
                for n in neighbors:
                    if n not in labels:
                        ln = next(coords_label)
                        labels[n] = ln
                        coords[ln] = n
                    else:
                        ln = labels[n]
                    csr_row.append(lp)
                    csr_col.append(ln)

        # create sparse matrix
        csr_dim = (len(csr_row), len(csr_col))
        csr_data = [1,] * len(csr_row)
        assert(csr_dim[0] == csr_dim[1])
        m = csr_matrix((csr_data, (csr_row, csr_col)), shape=csr_dim, dtype=np.uint8)
        print(len(csr_data))

        # calculate shortest distances
        dists, pred = csgraph.shortest_path(m, method='D',
                directed=False, unweighted=True, return_predecessors=True)
        dists_nonzero = np.logical_and(np.isfinite(dists), dists > 0)
        for i, j in zip(*np.where(dists_nonzero)):
            print('%02d: %d%s -> %d%s' % (dists[i, j], i, coords[i], j, coords[j]))

        start = 380
        dest = 366
        while dists[dest, start] > 0:
            n = pred[dest, start]
            print('%d%s -> %d%s' % (start, coords[start], n, coords[n]))#, dists[n, dest]))
            start = n

        #02: 380(30, 11) -> 373(30, 9)
        # 10: 380(30, 11) -> 376(30, 15)
        print(pred[380, 380])
        #print(sh[np.isfinite(sh)])
        #for i in np.arange(sh.shape[0]):
            #for j in np.arange(sh.shape[1]):
        
        #print(self.tostring(overlay_units = False))
        self.overlay(ubak)

        ## calculate coordinates of spaces
        ##scoords = set(zip(*np.where(self.board == '.')))
        #ucoords = set([(u.posy, u.posx) for u in self.units])
        #scoords -= ucoords
        #scoords = dict(enumerate(sorted(scoords)))
        #print(scoords)



        #for u in self.units:
            #u.move(self)



# ------------------------------------------------
# read board
# ------------------------------------------------
b = Board(INPUT)
print(b)
print(repr(b))
b.tick()
b.plot()


#if DEBUG:
    #print_board(board, units)
    #plot_board(board, units)
sys.exit(0)

# ------------------------------------------------
# part 1
# ------------------------------------------------

# ------------------------------------------------
# part 2
# ------------------------------------------------

# vim:sts=4:sw=4:et:
