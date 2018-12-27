#!/usr/bin/env python3
import re
import sys
import itertools
import numpy as np
from progress.bar import IncrementalBar
from pprint import pprint
INPUTS = [ 'd17-input.txt', 'd17-input-example.txt' ]

DEBUG = False
PRINT_LINENO = False
INPUT = INPUTS[0] if DEBUG else INPUTS[0]

# ------------------------------------------------
# helpers
# ------------------------------------------------
class Segment:
    type_order = {'|': 10, '~': 20, '#': 30}

    def __init__(self, vrange, hrange, offset=(0, 0), stype='#'):
        self.i = vrange
        self.j = hrange
        self.offset = offset
        self.stype = stype
        if type(hrange) is tuple:
            self.align = 'h'
            assert(hrange[0] < hrange[1])
        elif type(vrange) is tuple:
            self.align = 'v'
            assert(vrange[0] < vrange[1])
        else:
            assert(False)

    def __repr__(self):
        return '<%s-%s:%s:%s:%s>' % (self.align, self.__class__.__name__.lower(), self.stype, self.i, self.j)

    def __lt__(self, other):
        # drawing order
        td = self.order - other.order
        if td != 0:
            return td < 0

        if self.align != other.align:
            return self.align > other.align

        if self.align == 'h':
            if self.i != other.i: return self.i < other.i
            else: return self.j < other.j
        else:
            if self.j != other.j: return self.j < other.j
            else: return self.i < other.i
        
        return False

    @property
    def order(self):
        return Segment.type_order.get(self.stype, 100)

    @property
    def top_left(self):
        if self.align == 'h':
            return (self.i, self.j[0])
        else:
            return (self.i[0], self.j)

    @property
    def bottom_right(self):
        if self.align == 'h':
            return (self.i, self.j[1])
        else:
            return (self.i[1], self.j)

    def draw(self, board):
        if self.align == 'h':
            board[self.i, self.j[0]:self.j[1]+1] = self.stype
        else:
            board[self.i[0]:self.i[1]+1, self.j] = self.stype

    def contains(self, point):
        i, j = point
        if self.align == 'h':
            if self.i != i or self.j[0] > j or self.j[1] < j:
                return False
            else:
                return True
        else:
            if self.j != j or self.i[0] > i or self.i[1] < i:
                return False
            else:
                return True

    def overlaps(self, other):
        if self.align == 'h' and other.align == 'h':
            return (other.i == self.i) and not (other.j[1] < self.j[0] or other.j[0] > self.j[1])
        elif self.align == 'v' and other.align == 'v':
            return (other.j == self.j) and not (other.i[1] < self.i[0] or other.i[0] > self.i[1])
        elif self.align == 'v' and other.align == 'h':
            return (other.j[0] <= self.j <= other.j[1]) and (self.i[0] <= other.i <= self.i[1])
        elif self.align == 'h' and other.align == 'v':
            return other.overlaps(self)
        else:
            assert(False)

    def set_offset(self, offset):
        adj = (self.offset[0] - offset[0], self.offset[1] - offset[1])
        if self.align == 'h':
            self.i = self.i + adj[0]
            self.j = (self.j[0]+adj[1], self.j[1]+adj[1])
        else:
            self.i = (self.i[0]+adj[0], self.i[1]+adj[0])
            self.j = self.j + adj[1]
        self.offset = offset

    @classmethod
    def overlap_check(self, segments):
        ''' Checks if two segments overlap.
        '''
        for a, b in itertools.combinations(segments, 2):
            if a.overlaps(b):
                print(a, 'overlaps with', b)

    @classmethod
    def adjust_offsets(self, segments, offset):
        for w in segments:
            w.set_offset(offset)

    @classmethod
    def area(self, segments):
        ''' Returns the topleft and bottom right points of the area
            that contains all the wall segments.
        '''
        w0 = segments[0]
        top_left = list(w0.top_left)
        bottom_right = list(w0.bottom_right)
        for w in segments:
            wtop_left = w.top_left
            wbottom_right = w.bottom_right
            top_left[0] = min(top_left[0], wtop_left[0])
            top_left[1] = min(top_left[1], wtop_left[1])
            bottom_right[0] = max(bottom_right[0], wbottom_right[0])
            bottom_right[1] = max(bottom_right[1], wbottom_right[1])
        return (top_left, bottom_right)

    @classmethod
    def make_fill(self, where, board):
        ''' Creates a fill segment.
        '''
        i, j = where

        # keep only horizontal segments on the same level with start
        hsegs = sorted([s for s in board.hsegs
            if s.align == 'h' and s.i == i], key=lambda s: s.j)

        # segments containing the start
        startsegs = [s for s in hsegs if s.stype in '~#' and s.contains(where)]
        if DEBUG:
            print('floor segments', segments)
        if not startsegs:
            return None
        #assert(len(startsegs) > 0)

        # create initial fill segment
        b = [min([s.j[0] for s in startsegs]), max([s.j[1] for s in startsegs])]
        fill = Segment(i-1, tuple(b), offset=startsegs[0].offset, stype='~')
        if DEBUG:
            print('original', fill)

        # expand fill segment
        lsegments = reversed([s for s in hsegs if s.j[1] < j])
        for s in lsegments:
            if s.j[1] + 1 >= b[0]: b[0] = s.j[0]
        rsegments = [s for s in hsegs if s.j[0] > j]
        for s in rsegments:
            if b[1] + 1 >= s.j[0]: b[1] = s.j[1]
        fill.j = tuple(b)
        if DEBUG:
            print('expanded', fill)

        # get the vertical segments overlapping the fill
        vsegs = [s for s in board.vsegs if s.align == 'v' and
                s.stype == '#' and s.overlaps(fill)]

        # horizontal segments to the left and right of the start
        lsegments = [s for s in vsegs if s.j < j]
        rsegments = [s for s in vsegs if s.j > j]

        # trim fill segment if needed
        if lsegments:
            b[0] = lsegments[-1].j
        if rsegments:
            b[1] = rsegments[0].j
        fill.j = tuple(b)
        if DEBUG:
            print('trimmed', fill)

        return fill

class Stream:
    ''' A stream is always flowing downwards.
    '''
    sn = 0

    def __init__(self, pos, board, upstream=None):
        self.start = pos
        self.end = (pos[0]+1, pos[1])
        self.b = board
        self.upstream = upstream
        self.ndown = 0
        self.sn = Stream.sn
        Stream.sn += 1

    def __repr__(self):
        psn = self.upstream.sn if self.upstream is not None else -1
        return '<s%02d dn:%d up=s%02d start=%s end=%s>' % (self.sn, self.ndown, psn, self.start, self.end)

    def __lt__(self, other):
        if self.ndown != other.ndown:
            return self.ndown < other.ndown
        else:
            return self.sn > other.sn
    
    def step(self):
        if self.ndown > 0:
            return []

        if self.start >= self.end:
            if self.upstream is not None:
                self.upstream.ndown -= 1
            self.b.streams.remove(self)
            return []

        if [s for s in self.b.hsegs if s.stype == '~' and s.contains(self.start)]:
            if self.upstream is not None:
                self.upstream.ndown -= 1
            self.b.streams.remove(self)
            return []

        i, j = self.end
        new_segments = []

        # use a vertical segment to find the floor the stream will hit
        # we start from the stream start, to account for the current position being submerged 
        floor_level = None
        vseg = Segment((self.start[0], self.b.dims[0]-1), j, offset=self.b.offset, stype='|')
        for s in self.b.hsegs:      # hsegs assumed to be sorted
            if s.stype in '~#' and vseg.overlaps(s):
                floor_level = s.i
                break

        # create fill segment
        fill = Segment.make_fill((floor_level, j), self.b)
        if fill is None:
            sand = Segment((self.start[0], self.b.dims[0]),  self.start[1], stype='|')
            new_segments.append(sand)

            if self.upstream is not None:
                self.upstream.ndown -= 1
            self.b.streams.remove(self)

            return new_segments
        else:
            new_segments.append(fill)

        # check for overflows - fill endpoints must fall on a wall
        border_left = [s for s in self.b.vsegs
                if s.stype == '#' and s.contains(fill.top_left)]
        border_right = [s for s in self.b.vsegs
                if s.stype == '#' and s.contains(fill.bottom_right)]
        overflow_up = not (self.start[0] < fill.i)
        overflow_left = not border_left
        overflow_right = not border_right

        if DEBUG:
            print('s%02d' % self.sn, fill, border_left, border_right)

        if overflow_up:
            return new_segments

        self.end = (fill.i-1, j)
        
        if not (overflow_left or overflow_right):
            return new_segments
        else:
            fill.stype = '|'
            if overflow_left:
                self.ndown += 1
                self.b.streams.append(Stream((fill.i, fill.j[0]-1), self.b, upstream=self))
            if overflow_right:
                self.ndown += 1
                self.b.streams.append(Stream((fill.i, fill.j[1]+1), self.b, upstream=self))

            # add sand in the downstream
            assert(self.start[1] == self.end[1])
            if fill.i > self.start[0]:
                sand = Segment((self.start[0], fill.i),  self.start[1], stype='|')
                new_segments.append(sand)

            return new_segments

class Board:
    ''' Class representing the board of the puzzle.
        All coordinates in the internal state are relative to self.offset.
    '''
    input_line_re = re.compile(r'(?P<d1>[xy])=(?P<r1>[\d]+), (?P<d2>[xy])=(?P<r2>[\d]+\.\.[\d]+)')
    def __init__(self, inputf, spring=(0, 500)):
        # read wall segments
        self.segments = []
        with open(inputf) as f:
            for ln, line in enumerate(f):
                m = Board.input_line_re.match(line)
                if not m:
                    print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
                    continue
                elif m['d1'] == 'y' and m['d2'] == 'x':
                    ry = int(m['r1'])
                    rx = tuple(map(int, m['r2'].split('..')))
                elif m['d1'] == 'x' and m['d2'] == 'y':
                    ry = tuple(map(int, m['r2'].split('..')))
                    rx = int(m['r1'])
                else:
                    print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
                    continue
                self.segments.append(Segment(ry, rx))
        assert(self.segments)

        # area and offset - absolute coords - account for left overflows in offset
        self.area = Segment.area(self.segments)
        self.offset = (self.area[0][0], self.area[0][1])

        # adjust offset for wall segments
        Segment.adjust_offsets(self.segments, self.offset)

        # horizontal and vertical segments
        self.hsegs = [w for w in self.segments if w.align == 'h']
        self.vsegs = [w for w in self.segments if w.align == 'v']

        # dims - relative coords - account for left/right overflows in dims
        self.dims = self.ocoords(self.area[1])
        self.dims = (self.dims[0]+1, self.dims[1]+3)

        # spring - move inside the segment area
        assert(spring[1] >= self.area[0][1] and spring[1] <= self.area[1][1])
        self.spring = self.ocoords(spring)
        if self.spring[0] < 0:
            self.spring = (0, self.spring[1])

        # streams
        self.streams = [Stream(self.spring, self)]

        # board
        self.board = None

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

    def step(self):
        self.streams.sort()

        # iterate on a copy, as stepping may add streams
        for s in self.streams.copy():
            self.hsegs.sort(key=lambda s: s.i)
            self.vsegs.sort(key=lambda s: s.j)
            new_segments = s.step()
            for seg in new_segments:
                self.segments.append(seg)
                if seg.align == 'h':
                    self.hsegs.append(seg)
                else:
                    self.vsegs.append(seg)

        # special cases
        self.streams.sort(key=lambda s: s.start)
        sp = None
        for s in self.streams.copy():
            if sp is not None and (sp.start == s.start or sp.end == s.start):
                self.streams.remove(s)
                continue
            sp = s


    def update(self, draw_streams=True):
        ''' Updates the board based on the segments.
            Tile counting should be done on the board contents.
        '''
        self.board = np.full(self.dims, ' ', dtype=np.unicode)
        for s in sorted(self.segments):
            s.draw(self.board)

        if draw_streams:
            for s in self.streams:
                if s.ndown == 0:
                    self.board[s.start[0], s.start[1]] = '&'
                    self.board[s.end[0], s.end[1]] = '*'
                else:
                    self.board[s.start[0], s.start[1]] = '/'
                    self.board[s.end[0], s.end[1]] = '/'
            self.board[self.spring[0], self.spring[1]] = 'X'

        if PRINT_LINENO:
            for i in range(self.board.shape[0]):
                s = list("%04d " % i)
                self.board[i, 0:len(s)] = s

    def tostring(self):
        if self.board is None:
            self.update()
        #s = '\n'.join(np.apply_along_axis(lambda s: ''.join(s), axis=1, arr=self.board[50:]))
        s = '\n'.join(np.apply_along_axis(lambda s: ''.join(s), axis=1, arr=self.board))
        return s

# ------------------------------------------------
# read board
# ------------------------------------------------
b = Board(INPUT)
print(repr(b))

# ------------------------------------------------
# part 1 and 2
# ------------------------------------------------
nsteps = 1100
print_after = 30000
bar = IncrementalBar(max=nsteps)
for i in range(nsteps):
    b.step()
    bar.next()
    if DEBUG or i >= print_after:
        print('step_%03d' % i)
        pprint(b.streams)
        print(10*'-')
        b.update()
        print(b)

b.update(draw_streams=False)
water = sum((b.board == '~').flatten())
sand = sum((b.board == '|').flatten())
b.update()
print(b)
print('%d + %d = %d' % (water, sand, water+sand))

# vim:sts=4:sw=4:et:
