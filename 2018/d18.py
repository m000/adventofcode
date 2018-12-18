#!/usr/bin/env python3
import re
import sys
import hashlib
import itertools
import numpy as np
from collections import Counter
from matplotlib import pyplot
from pprint import pprint
INPUTS = [ 'd18-input.txt', 'd18-input-example.txt']

DEBUG = False
INPUT = INPUTS[1] if DEBUG else INPUTS[0]

# ------------------------------------------------
# helpers
# ------------------------------------------------
class Board:
    ''' Class representing the board of the puzzle.
        All coordinates in the internal state are relative to self.offset.
    '''
    input_line_re = re.compile(r'([.#|]+)')
    hashf = hashlib.sha1

    def __init__(self, inputf):
        # read dimensions
        ldims = []
        with open(inputf) as f:
            for ln, line in enumerate(f):
                m = self.input_line_re.match(line)
                if not m:
                    print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
                    continue
                else:
                    ldims.append( (ln, m.span()[1]) )
            self.dims = (max([d[0] for d in ldims])+1, max([d[1] for d in ldims]))

        # read data
        self.board = np.full(self.dims, '.', dtype=np.unicode)
        with open(inputf) as f:
            for ln, line in enumerate(f):
                m = self.input_line_re.match(line)
                if not m:
                    print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
                    continue
                else:
                    self.board[ln] = list(m.group(0))

        # initialize the rest
        self.ts = 0

    def __repr__(self):
        return '%s<dims=%s, ts=%d, value=%d>' % (self.__class__.__name__, self.dims, self.ts, self.value())

    def __str__(self):
        return self.tostring()

    def tostring(self):
        s = '\n'.join(np.apply_along_axis(lambda s: ''.join(s), axis=1, arr=self.board))
        return s

    def plot(self):
        # https://matplotlib.org/examples/color/colormaps_reference.html
        scolor = 0      # space
        tcolor = 66     # tree
        lcolor = 255    # lumperyard

        imdata = np.full(self.board.shape, scolor, dtype=np.uint8)
        #----------------------
        coords = np.where(self.board == '#')
        imdata[coords] = lcolor
        #----------------------
        coords = np.where(self.board == '|')
        imdata[coords] = tcolor
        #----------------------
        img = pyplot.imshow(imdata, cmap='Paired')
        img.get_figure().suptitle(repr(self))
        pyplot.show()

    def value(self):
        c = Counter(self.board.flatten())
        return c['|'] * c['#']

    def area(self, i, j):
        assert( i <= self.board.shape[0]+1 and j <= self.board.shape[1] )
        ir = (max(0, i-1), min(self.board.shape[0], i+2))
        jr = (max(0, j-1), min(self.board.shape[1], j+2))
        return self.board[ir[0]:ir[1], jr[0]:jr[1]]

    def tick(self):
        board = self.board.copy()
        for i, j in itertools.product(range(self.board.shape[0]), range(self.board.shape[1])):
            acre = self.board[i, j]
            area = self.area(i, j)
            c = Counter(area.flatten())
            c[acre] -= 1

            if acre == '.' and c['|'] >= 3:
                board[i, j] = '|'
            elif acre == '|' and c['#'] >= 3:
                board[i, j] = '#'
            elif acre == '#' and (c['#'] == 0 or c['|'] == 0):
                board[i, j] = '.'
        self.board = board
        self.ts += 1

    def checksum(self):
        return self.hashf(str(self).encode('utf-8')).hexdigest()

    def find_period(self, max_tick=1000):
        bak = (self.board.copy(), self.ts)
        checksums = set()
        timestamps = {}
        print('Searching for periodic pattern: ', end='', flush=True)
        for t in range(max_tick):
            if t % 100  == 0:
                print('%03d' % t, end='..', flush=True)

            c = self.checksum()
            if c in checksums:
                print('%03d found!' % t)
                ret = (timestamps[c], self.ts-timestamps[c])
                self.board, self.ts = bak
                return ret
                break
            else:
                checksums.add(c)
                timestamps[c] = self.ts
            self.tick()
        self.board, self.ts = bak
        return None

# ------------------------------------------------
# part 1
# ------------------------------------------------
b = Board(INPUT)
while b.ts < 10:
    if DEBUG:
        print(repr(b))
        print(b)
        print('')
        b.plot()
    b.tick()
print(repr(b))
print(b)
b.plot()

# ------------------------------------------------
# part 2
# ------------------------------------------------
b = Board(INPUT)

# find period
period = b.find_period()
assert(period is not None)

# estimate board
s, p = period
n = 1000000000
ticks = s + ((n - s) % p)
print('Estimating board after %d ticks...' % n, end='', flush=True)
while b.ts < ticks:
    if DEBUG:
        print(repr(b))
        print(b)
        print('')
        b.plot()
    b.tick()
print('')
print(repr(b))
print(b)
b.plot()

# vim:sts=4:sw=4:et:
