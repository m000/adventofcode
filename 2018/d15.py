#!/usr/bin/env python3
import re
import sys
import itertools
import numpy as np
import networkx as nx
from matplotlib import pyplot
from pprint import pprint
INPUTS = [ 'd15-input.txt',
        'd15-input-example1.txt', 'd15-input-example2.txt', 'd15-input-example3.txt',
        'd15-input-example4.txt', 'd15-input-example5.txt', 'd15-input-example6.txt',
        'd15-input-test1.txt', 'd15-input-test2.txt', 'd15-input-test3.txt',
        'd15-input-test4.txt', 'd15-input-test5.txt', 'd15-input-test6.txt',
        'd15-input-test7.txt', ]

DEBUG = False
DEBUG_STEP = False
INPUT = INPUTS[13] if DEBUG else INPUTS[0]

# ------------------------------------------------
# constants and global state
# ------------------------------------------------
units_max = 1000
units_re = r'([GE])'
units_hp = {'G': 200, 'E': 200}
units_ap = {'G': 3, 'E': 3}

# ------------------------------------------------
# helpers
# ------------------------------------------------
hr = lambda s: ('--- %s ' % s).ljust(70, '-')

class Unit:
    def __init__(self, upos, utype, board):
        self.board = board
        self.i, self.j = upos
        self.type = utype
        self.hp = units_hp[self.type]
        self.ap = units_ap[self.type]
        self.id = next(self.board.units_id[self.type])

    def __str__(self):
        return '%s[%s, hp=%03d, ap=%d]' % (
                self.uid, self.pos, self.hp, self.ap)

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return (self.i, self.j) < (other.i, other.j)

    @property
    def uid(self):
        return '%s%d' % (self.type, self.id)

    @property
    def pos(self):
        return (self.i, self.j)

    @property
    def posxy(self):
        return (self.j, self.i)

    @property
    def neighbors(self):
        ''' Returns neighbouring tiles coordinates in reading order.
            Neighbours returned are guaranteed to be available for movement.
        '''
        n = [ (self.i-1, self.j), (self.i, self.j-1), (self.i, self.j+1), (self.i+1, self.j), ]
        return list(filter(self.board.is_open, n))

    @property
    def enemies(self):
        return filter(lambda u: u.type != self.type, self.board.units)

    def add_to_graph(self):
        ''' Add the position of the unit to the graph as open tile.
        '''
        self.board.graph.add_node(self.pos) # needed in case unit is surrounded
        for n in self.neighbors:
            if self.board.typeof(n) != '#':
                self.board.graph.add_edge(self.pos, n, weight=1)

    def remove_from_graph(self):
        ''' Remove the position of the unit from the graph.
        '''
        self.board.graph.remove_node(self.pos)

    def get_targets(self):
        ''' Returns the movement and attack targets for this unit.
            Movement targets are tiles that have an enemy in attack range.
            Attack targets are enemy units currently in range.
        '''
        move_targets = set()
        attack_targets = []

        # temporarily remove us from board
        # this allows our current tile to be listed as neighbor of enemies
        self.board.board[self.i, self.j] = '.'

        for e in self.enemies:
            en = list(e.neighbors)
            move_targets.update(en)
            if self.pos in en:
                attack_targets.append(e)

        self.board.board[self.i, self.j] = self.type
        return (move_targets, attack_targets)

    def move(self, move_to):
        print('%s moved to %s' % (self, move_to), file=sys.stderr)

        # make sure node is in the graph
        if self.pos not in self.board.graph.nodes:
            self.add_to_graph()

        # mark position as open on the board
        self.board.board[self.i, self.j] = '.'

        # move to new position and update graph/board
        self.i, self.j = move_to
        self.remove_from_graph()
        self.board.board[self.i, self.j] = self.type

    def attack(self, other):
        other.hp -= self.ap
        if other.hp <= 0:
            print('%s killed %s' % (self, other), file=sys.stderr)

            # add unit to graph as open tile
            assert(other.pos not in self.board.graph.nodes)
            other.add_to_graph()

            # remove unit from board and units list
            self.board.board[other.i, other.j] = '.'
            self.board.units.remove(other)
        else:
            print('%s attacked %s' % (self, other), file=sys.stderr)

    def action(self):
        # add to board and compute all distances to open tiles
        self.add_to_graph()
        dists = nx.single_source_shortest_path_length(self.board.graph, self.pos)

        # get move/attack targets
        move_targets, attack_targets = self.get_targets()
        if attack_targets:
            hpmin = min([e.hp for e in attack_targets])
            tgt_a = min([e for e in attack_targets if e.hp == hpmin])
            self.attack(tgt_a)
            self.remove_from_graph()
            return

        # keep only target tiles in distances dict
        dists = { p: d for p, d in dists.items() if p in move_targets }

        # blocked
        if not dists:
            print('%s skipped turn' % self, file=sys.stderr)
            self.remove_from_graph()
            return

        # find the minimum distance
        mindist = min(dists.values())

        # keep only target tiles with the minimum distance
        dists = { p: d for p, d in dists.items() if d == mindist }

        # get the first target tile in reading order
        tgt_m = min(dists)

        # there may be different paths to the target tile!
        tgt_path = None
        for n in self.neighbors:
            p = nx.shortest_path(self.board.graph, n, tgt_m)
            if len(p) == mindist:
                tgt_path = p
                break
        assert(tgt_path is not None)

        # move - no need to remove from board
        self.move(tgt_path[0])

        # if mindist was 1, we are now in range
        if mindist == 1:
            move_targets, attack_targets = self.get_targets()
            hpmin = min([e.hp for e in attack_targets])
            tgt_a = min([e for e in attack_targets if e.hp == hpmin])
            self.attack(tgt_a)
            return

class Board:
    def __init__(self, inputf):
        # read dimensions
        ldims = []
        with open(inputf) as f:
            for ln, line in enumerate(f):
                ldims.append( (ln, len(line.rstrip())) )
        self.dims = (max([d[0] for d in ldims])+1, max([d[1] for d in ldims]))

        # reset unit ids
        self.units_id = {utype: iter(range(units_max)) for utype in units_hp}

        # read data
        self.board = np.empty(self.dims, dtype=np.unicode)
        self.units = []
        with open(inputf) as f:
            for ln, line in enumerate(f):
                line = line.rstrip()
                if not line.lstrip(): continue
                elif line.lstrip().startswith('//'): continue
                self.board[ln] = list(line.ljust(self.dims[1]))
                for um in re.finditer(units_re, line):
                    upos, utype = (ln, um.span()[0]), um.group(0)
                    u = Unit(upos, utype, self)
                    self.board[u.i, u.j] = u.type
                    self.units.append(u)
        self.units.sort()

        # initialize graph
        # Note: SciPy also has support for shortest path algorithms.
        #       However, it requires explicit mapping of nodes to arithmetic
        #       labels, and representing the graph as a NxN csr matrix.
        #       Updating the matrix is also a pain because of the explicit
        #       mapping to arithmetic labels.
        #       Networkx makes it much simpler to maintain a consistent
        #       state of the simulation.
        self.init_graph()

        # initialize other state
        self.round = 0

    def typeof(self, p):
        ''' Returns type of tile in coords p.
        '''
        return self.board[p[0], p[1]]

    def in_bounds(self, p):
        ''' Returns if coords p are in bounds.
        '''
        return (0 <= p[0] < self.dims[0]) and (0 <= p[1] < self.dims[1])

    def is_open(self, p):
        ''' Returns if coords p are in bounds and open.
        '''
        return self.in_bounds(p) and self.typeof(p) == '.'

    def init_graph(self):
        self.graph = nx.Graph()
        neighbors = ((-1, 0), (0, -1), (0, 1), (1, 0))

        for i, j in itertools.product(range(self.dims[0]), range(self.dims[1])):
            p = (i, j)
            if self.board[i, j] != '.':
                continue
            for di, dj in neighbors:
                n = (i + di, j + dj)
                if self.in_bounds(n) and self.typeof(n) == '.':
                    self.graph.add_edge(p, n, weight=1)

    def __repr__(self):
        return '%s<%dx%d, %d units: %s>' % (self.__class__.__name__,
                self.dims[1], self.dims[0], len(self.units), self.units)

    def __str__(self):
        return '\n'.join(np.apply_along_axis(lambda s: ''.join(s), axis=1, arr=self.board))

    def count(self, utype=None):
        if utype == None:
            return len(self.units)
        else:
            return len([u for u in self.units if u.type == utype])

    def plot(self):
        # https://matplotlib.org/examples/color/colormaps_reference.html
        wcolor = 255    # wall
        scolor = 0      # space
        Ecolor = 66     # elf
        Gcolor = 110    # gnome
        rcolor = 220    # in range

        imdata = np.full(self.board.shape, wcolor, dtype=np.uint8)
        #----------------------
        coords = np.where(self.board == '.')
        imdata[coords] = scolor
        #----------------------
        inrange = set()
        for u in self.units:
            inrange.update(u.neighbors)
        coords = tuple(zip(*inrange))
        imdata[coords] = rcolor
        #----------------------
        coords = np.where(self.board == 'G')
        imdata[coords] = Gcolor
        #----------------------
        coords = np.where(self.board == 'E')
        imdata[coords] = Ecolor
        #----------------------
        img = pyplot.imshow(imdata, cmap='Paired')
        img.get_figure().suptitle(self.score, fontfamily='monospace')
        pyplot.show()

    @property
    def finished(self):
        return len(set([u.type for u in self.units])) < 2

    @property
    def score(self):
        s = {}
        for u in self.units:
            if u.type not in s:
                s[u.type] = 0
            s[u.type] += u.hp
        return '\n'.join([ '%s(%03d)(%02d):[%3d x %4d = %6d]' %
            (k, units_hp[k], units_ap[k], self.round, v, v*self.round)
            for k, v in sorted(s.items())])

    def tick(self, quiet=False):
        print(hr('round %04d' % self.round), file=sys.stderr)

        # sort units
        self.units.sort()

        # activate units - use a copy as units may die while looping
        for u in self.units.copy():
            if (u.hp <= 0):
                continue
            if self.finished:
                print(self.score)
                print('')
                self.plot()
                return
            if DEBUG_STEP:
                self.plot()
            u.action()

        # update after tick
        if not quiet:
            self.plot()
        self.round += 1

# ------------------------------------------------
# part 1
# ------------------------------------------------
b = Board(INPUT)
b.plot()
while not b.finished:
    b.tick(quiet=True)

# ------------------------------------------------
# part 2
# ------------------------------------------------
units_ap_bak = units_ap.copy()
while True:
    units_ap['E'] += 1
    b = Board(INPUT)
    b.plot()
    ne = b.count('E')
    while not b.finished:
        b.tick(quiet=True)
        if b.count('E') < ne:
            print('Elf killed. Aborting simulation at round %d.' % (b.round), file=sys.stderr)
            b.plot()
            break
    if b.finished:
        break
units_ap = units_ap_bak

# vim:sts=4:sw=4:et:
