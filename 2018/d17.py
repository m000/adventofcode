#!/usr/bin/env python3
import re
import sys
import numpy as np
import itertools
from scipy.sparse import csr_matrix
from matplotlib import pyplot
from pprint import pprint
INPUTS = [ 'd17-input.txt', ]

DEBUG = True
INPUT = INPUTS[0] if DEBUG else INPUTS[0]

# ------------------------------------------------
# constants
# ------------------------------------------------
line_re = re.compile(r'(?P<d1>[xy])=(?P<r1>[\d]+), (?P<d2>[xy])=(?P<r2>[\d]+\.\.[\d]+)')

# ------------------------------------------------
# helpers
# ------------------------------------------------
class Board:
    ''' Class representig the board of the puzzle.
        All coordinates in the internal state are relative to self.offset.
    '''
    def __init__(self, inputf, spring=(0, 500)):
        # read dimensions
        ldims = []
        with open(inputf) as f:
            for ln, line in enumerate(f):
                m = line_re.match(line)
                if not m:
                    print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
                    continue
                elif m['d1'] == 'y' and m['d2'] == 'x':
                    ry = m['r1']
                    rx = m['r2'].split('..')
                    ldims.append( (int(ry), int(rx[1])) )
                elif m['d1'] == 'x' and m['d2'] == 'y':
                    ry = m['r2'].split('..')
                    rx = m['r1']
                    ldims.append( (int(ry[1]), int(rx)) )
                else:
                    print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
                    continue

            # calculate offset - must include the spring location
            self.offset = (min([d[0] for d in ldims]), min([d[1] for d in ldims]))
            self.offset = (min(spring[0], self.offset[0]), min(spring[1], self.offset[1]))

            # calculate dims - offset-relative
            self.dims = self.ocoords((max([d[0] for d in ldims])+1, max([d[1] for d in ldims])+1))

            # calculate spring - offset-relative
            self.spring = self.ocoords(spring)

            # initialize streams
            self.streams = [self.spring,]

        # read data
        self.board = np.full(self.dims, ' ', dtype=np.unicode)
        with open(inputf) as f:
            for ln, line in enumerate(f):
                m = line_re.match(line)
                if not m:
                    print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
                    continue
                elif m['d1'] == 'y' and m['d2'] == 'x':
                    ry = (int(m['r1']), int(m['r1'])+1)
                    rx = m['r2'].split('..')
                    rx = (int(rx[0]), int(rx[1])+1)
                elif m['d1'] == 'x' and m['d2'] == 'y':
                    ry = m['r2'].split('..')
                    ry = (int(ry[0]), int(ry[1])+1)
                    rx = (int(m['r1']), int(m['r1'])+1)
                else:
                    print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
                    continue
                ry = (ry[0]-self.offset[0], ry[1]-self.offset[0])
                rx = (rx[0]-self.offset[1], rx[1]-self.offset[1])
                for i, j in itertools.product(range(*ry), range(*rx)):
                    self.board[i, j] = '#'

    def ocoords(self, p):
        ''' Translate to offset-based coordinates.
        '''
        return (p[0]-self.offset[0], p[1]-self.offset[1])

    def gcoords(self, p):
        ''' Translate to global coordinates.
        '''
        return (p[0]+self.offset[0], p[1]+self.offset[1])

    def __repr__(self):
        return '%s<dims=%s, offset=%s, spring=%s>' % (self.__class__.__name__,
                self.dims, self.offset, self.spring)

    def __str__(self):
        return self.tostring()

    def overlay(self, items, f=None, noassert=False):
        if f is not None:
            items = map(f, items)
        replaced = []
        for pos, o, valid in items:
            i, j = pos[0], pos[1]
            v = self.board[i, j]
            assert(v == valid or valid is None)
            self.board[i, j] = o
            replaced.append( (pos, v, o) )
        return replaced

    def tostring(self):
        sbak = self.overlay([self.spring], lambda u: (u, '+', None))
        wbak = self.overlay(self.streams, lambda u: (u, '*', None))
        s = '\n'.join(np.apply_along_axis(lambda s: ''.join(s), axis=1, arr=self.board))
        self.overlay(wbak)
        self.overlay(sbak)
        return s

    def plot(self):
        # https://matplotlib.org/examples/color/colormaps_reference.html
        wcolor = 255    # wall
        scolor = 0      # space
        #Ecolor = 66     # elf
        #Gcolor = 110    # gnome
        #rcolor = 220    # in range
        cprops = {
                'color': 'white',
                'fontweight': 'black',
                'fontfamily': 'monospace',
                'horizontalalignment': 'center',
                'verticalalignment': 'center',
        }
        imdata = np.full(self.board.shape, scolor, dtype=np.uint8)
        #----------------------
        coords = np.where(self.board == '#')
        imdata[coords] = wcolor
        #----------------------
        #inrange = self.in_range()
        #coords = tuple(zip(*inrange.keys()))
        #imdata[coords] = rcolor
        #----------------------
        #coords = tuple(zip(*[(u.posy, u.posx) for u in self.units if u.type == 'G']))
        #imdata[coords] = Gcolor
        #----------------------
        #coords = tuple(zip(*[(u.posy, u.posx) for u in self.units if u.type == 'E']))
        #imdata[coords] = Ecolor
        #----------------------
        img = pyplot.imshow(imdata, cmap='Paired')
        pyplot.show()

    def fill_all_streams(self, i=0):
        # fill individual streams
        all_streams = set()
        for s in self.streams:
            all_streams.update(self.fill_stream(s))

        # adjust streams that became submerged
        orphan_adjust = 1
        for si, s in enumerate(all_streams):
            sbak = s
            u = self.board[s[0]-1, s[1]]
            l = self.board[s[0], s[1]-1]
            r = self.board[s[0], s[1]+1]
            h = self.board[s[0], s[1]]
            print('before', s, [u, l, r, h])

            while self.board[s[0], s[1]] == '~':
                s = (s[0]-1, s[1])

            # check if adjustment made this an orphan
            u = self.board[s[0]-1, s[1]]
            l = self.board[s[0], s[1]-1]
            r = self.board[s[0], s[1]+1]
            h = self.board[s[0], s[1]]
            print('after', s, [u, l, r, h])

            if u != '|' and l != '|' and r != '|':
                print('orphan')
                adjusted = True
                while self.board[s[0], s[1]] != '|':
                    s = (s[0], s[1]+orphan_adjust)
                orphan_adjust *= -1

            u = self.board[s[0]-1, s[1]]
            l = self.board[s[0], s[1]-1]
            r = self.board[s[0], s[1]+1]
            h = self.board[s[0], s[1]]
            print('finally', s, [u, l, r, h])

            if sbak != s:
                all_streams.remove(sbak)
                all_streams.add(s)

        self.streams = list(all_streams)
        print(self)

            
    def fill_stream(self, stream):
        ''' Rises the water level by one in the next location to be filled.
        '''
        i, j = stream

        # column where the stream drops
        col = self.board[i+1:, j]

        # floor where drop stops and fill with clay
        floori = i + 1 + np.where(col != ' ')[0][0]
        self.board[i:floori-1, j] = '|'

        # floor row and flood row
        floor = self.board[floori, :]
        flood = self.board[floori-1, :]

        # fill to left and right
        leftj = rightj = j
        while flood[leftj] in ' |' and floor[leftj] in '#~':
            leftj -= 1
        while flood[rightj] in ' |' and floor[rightj] in '#~':
            rightj += 1

        # fill with water or clay
        if flood[leftj] == '#' and flood[rightj] == '#':    # no overflow
            flood[leftj+1:rightj] = '~'
            return [(floori-2, j)]
        elif flood[leftj] != '#' and flood[rightj] != '#':  # overflow both
            flood[leftj+1:rightj] = '|'
            return [(floori-1, leftj), (floori-1, rightj)]
        elif flood[leftj] == '#':                           # overflow right
            flood[leftj+1:rightj] = '|'
            return [(floori-1, rightj)]
        elif flood[rightj] != '#':                          # overflow left
            flood[leftj+1:rightj] = '|'
            return [(floori-1, leftj)]

# ------------------------------------------------
# read board
# ------------------------------------------------
b = Board(INPUT)
print(repr(b))
#b.tick()
#b.plot()
for i in range(60):
    b.fill_all_streams(i)


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
