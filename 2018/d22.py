#!/usr/bin/env python3
import sys
import re
import itertools
import hashlib
import os
import numpy as np
from pprint import pprint
from progress.bar import IncrementalBar

CACHE_DIR = 'd22_cache'
INPUTS = [ 'd22-input.txt', 'd22-input-example.txt']
DEBUG = False
INPUT = INPUTS[1] if DEBUG else INPUTS[0]

# ------------------------------------------------
# Class modeling the cave.
# ------------------------------------------------
class Cave:
    x0_factor = 48271
    y0_factor = 16807
    errosion_mod = 20183
    def __init__(self, target, max_depth, max_width=None):
        self.target = (target[1], target[0])
        self.max_depth = max_depth
        self.max_width = max_width if max_width is not None else self.target[1]
        self.dims = (self.max_depth+1, self.max_width+1)

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
#c = Cave(target, depth, 3*target[0])
#print(repr(c))

# vim:sts=4:sw=4:et:
