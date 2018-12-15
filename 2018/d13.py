#!/usr/bin/env python3
import re
import sys
import numpy
from collections import Counter
from matplotlib import pyplot
INPUTS = [ 'd13-input.txt', 'd13-input-example1.txt', 'd13-input-example2.txt', 'd13-input-test0.txt' ]

DEBUG = False
INPUT = INPUTS[3] if DEBUG else INPUTS[0]

# ------------------------------------------------
# useful constants
# ------------------------------------------------
carts_re = r'([<>^v])'
carts_road = { '<': '-', '>': '-', '^': '|', 'v': '|' }
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
def read_dimensions(inputf):
    ldims = []
    with open(inputf) as f:
        for ln, line in enumerate(f):
            ldims.append( (ln, len(line.rstrip())) )
    return (max([d[0] for d in ldims])+1, max([d[1] for d in ldims]))

def print_board(board, carts, crashes=[]):
    road_bak = []
    for pos, d, nit in carts:
        road_bak.append( (pos, board[pos[0], pos[1]]) )
        board[pos[0], pos[1]] = d
    for pos in crashes:
        road_bak.append( (pos, board[pos[0], pos[1]]) )
        board[pos[0], pos[1]] = 'X'
    numpy.apply_along_axis(lambda s: print(''.join(s)), axis=1, arr=board)
    for pos, r in road_bak:
        board[pos[0], pos[1]] = r

def plot_board(board, carts, crashes=[], stride=2):
    icolor = 0
    rcolor = 50
    bcolor = 100
    cprops = {
            'color': 'white',
            'fontweight': 'black',
            'fontfamily': 'monospace',
            'horizontalalignment': 'center',
            'verticalalignment': 'center',
    }

    imshape = [stride*d for d in board.shape]
    imdata = numpy.full(imshape, bcolor, dtype=numpy.uint8)
    #----------------------
    coords = tuple(numpy.multiply(numpy.where(board == '/'), stride))
    imdata[coords] = rcolor
    #----------------------
    coords = tuple(numpy.multiply(numpy.where(board == '\\'), stride))
    imdata[coords] = rcolor
    #----------------------
    coords = tuple(numpy.multiply(numpy.where(board == '|'), stride))
    for i in range(-stride+1, stride):
        imdata[(numpy.add(coords[0], i), coords[1])] = rcolor
    #----------------------
    coords = tuple(numpy.multiply(numpy.where(board == '-'), stride))
    for i in range(-stride+1, stride):
        imdata[(coords[0], numpy.add(coords[1], i))] = rcolor
    #----------------------
    coords = tuple(numpy.multiply(numpy.where(board == '+'), stride))
    for i in range(-stride+1, stride):
        for j in range(-stride+1, stride):
            if i == 0 or j == 0:
                imdata[(numpy.add(coords[0], i), numpy.add(coords[1], j))] = rcolor
            else:
                #imdata[(numpy.add(coords[0], i), numpy.add(coords[1], j))] = (icolor + rcolor) // 2
                pass
    imdata[coords] = icolor
    #----------------------
    for pos, d, nits in carts:
        pyplot.text(stride*pos[1], stride*pos[0], d, **cprops)
    #----------------------
    for pos in crashes:
        pyplot.text(stride*pos[1], stride*pos[0], 'X', **cprops)
    #----------------------

    img = pyplot.imshow(imdata, cmap='Dark2')
    pyplot.show()

def tick_cart(board, c):
    pos, d, nit = c

    # update direction
    t = board[pos[0], pos[1]]
    if t == '+':
        (d, nit) = carts_iturn[d+nit]
    elif t == '/' or t == '\\':
        d = carts_turn[d+t]

    # update position
    if d == '<':    pos = (pos[0], pos[1]-1)
    elif d == '>':  pos = (pos[0], pos[1]+1)
    elif d == '^':  pos = (pos[0]-1, pos[1])
    elif d == 'v':  pos = (pos[0]+1, pos[1])
    else:           assert(False)

    return (pos, d, nit)

def tick(board, carts, stop_at=None):
    # Several tricky parts:
    #   - Collisions must be checked after every cart update, rather
    #     than after all carts have been updated.
    #   - Crashed carts need to be removed asap. Use a variable as
    #     index rather than using an enumeration of the list.
    #   - When removing carts before the current index, we need to
    #     adjust the index.
    carts.sort()
    crashes = set()
    i = 0
    while i < len(carts):
        c = tick_cart(board, carts[i])
        crashed = [j for j, jc in enumerate(carts) if j != i and jc[0] == c[0]]
        carts[i] = c
        if crashed:
            # remove all crashed
            crashed.append(i)
            crashed.sort(reverse=True)
            for j in crashed:
                if not j > i:
                    i -= 1
                crashes.add(carts[j][0])
                del carts[j]
        i += 1

    if (crashes or DEBUG or True):
        print('%d carts remaining: %s.' % (len(carts), _c(carts)))

    if DEBUG:
        print_board(board, carts, crashes)
        plot_board(board, carts, crashes)

    return (carts, crashes)

# ------------------------------------------------
# read board and carts
# ------------------------------------------------
dims = read_dimensions(INPUT)
board = numpy.empty(dims, dtype=numpy.unicode)
carts = []
with open(INPUT) as f:
    for ln, line in enumerate(f):
        line = line.rstrip()
        if not line.lstrip(): continue
        board[ln] = list(line.ljust(dims[1]))
        for cm in re.finditer(carts_re, line):
            position, direction, next_iturn = (ln, cm.span()[0]), cm.group(0), 'l'
            board[position[0], position[1]] = carts_road[direction]
            carts.append( (position, direction, next_iturn) )
    carts.sort()

_c = lambda cl: [(tuple(c[0][::-1]), c[1], c[2]) for c in cl]
print('%d carts remaining: %s.' % (len(carts), _c(carts)))
if DEBUG:
    print_board(board, carts)
    plot_board(board, carts)

# ------------------------------------------------
# part 1
# ------------------------------------------------
i = 0
while len(carts) > 1:
    if DEBUG:
        print('\nafter tick %d' % i)
    carts, crashes = tick(board, carts)
    if crashes: break
    i += 1
carts.sort()
print('')
print('First crash: tick=%d pos=%s' % (i, list(map(lambda t: t[::-1], crashes))))
print('%d carts remaining: %s.' % (len(carts), _c(carts)))
print_board(board, carts, crashes)
plot_board(board, carts, crashes)

# ------------------------------------------------
# part 2
# ------------------------------------------------
while len(carts) > 1:
    if DEBUG:
        print('\nafter tick %d' % i)
    carts, crashes = tick(board, carts)
    i += 1
assert(len(carts) <= 1)
carts.sort()
print('')
print('Last crash: tick=%d pos=%s' % (i, list(map(lambda t: t[::-1], crashes))))
print('%d carts remaining: %s.' % (len(carts), _c(carts)))
print_board(board, carts, crashes)
plot_board(board, carts, crashes)

# vim:sts=4:sw=4:et:
