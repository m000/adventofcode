#!/usr/bin/env python3
import sys
import numpy as np
from pprint import pprint

INPUTS = ['d20-input.txt', 'd20-input-example1.txt']
DEBUG = False
INPUT = INPUTS[1] if DEBUG else INPUTS[0]

# ------------------------------------------------
# helpers
# ------------------------------------------------
def reader(filename):
    with open(filename) as f:
        while True:
            c = f.read(1)
            if c:
                yield c
            else:
                return

class Map:
    dims = (201, 201)
    start = [100, 100]
    def __init__(self):
        self.m = np.full(Map.dims, ' ', dtype=np.unicode)
        self.d = np.full(Map.dims, -1, dtype=np.int32)
        self.m[:,0::2] = '?'
        self.m[0::2,:] = '?'
        self.m[0::2,0::2] = '#'
        self.p = Map.start
        self.set(Map.start, 'X')
        self.setd(Map.start, 0)

    def set(self, t, w):
        self.m[t[0], t[1]] = w

    def get(self, t):
        return self.m[t[0], t[1]]

    def setd(self, t, v):
        self.d[t[0], t[1]] = v

    def getd(self, t):
        return self.d[t[0], t[1]]

    def move(self, direction):
        assert(direction in 'EWNS')
        p = self.p
        d = self.getd(p)

        if direction == 'E':
            p[1] += 1; self.set(p, '|')
            p[1] += 1; self.set(p, 'o')
        elif direction == 'W':
            p[1] -= 1; self.set(p, '|')
            p[1] -= 1; self.set(p, 'o')
        elif direction == 'N':
            p[0] -= 1; self.set(p, '-')
            p[0] -= 1; self.set(p, 'o')
        elif direction == 'S':
            p[0] += 1; self.set(p, '-')
            p[0] += 1; self.set(p, 'o')

        dnew = d+1 if self.getd(p) < 0 else min(d+1, self.getd(p))
        self.setd(p, dnew)

    def finalize(self):
        self.m[np.where(self.m == ' ')] = '#'
        self.m[np.where(self.m == '?')] = '#'
        self.m[np.where(self.m == 'o')] = '.'

    def tostring(self, p = None):
        if p is None:
            p = self.p
        b = self.get(p)
        self.set(p, '*')
        s = '\n'.join(np.apply_along_axis(lambda s: ''.join(s), axis=1, arr=self.m))
        self.set(p, b)
        return s

    def __str__(self):
        return self.tostring()

# ------------------------------------------------
# process input
# ------------------------------------------------
ir = reader(INPUT)
m = Map()
context = []
for i, c in enumerate(ir):
    print(i, c)
    if c == '(':
        context.append(tuple(m.p))
    elif c == ')':
        m.p = list(context.pop())
    elif c == '|':
        m.p = list(context[-1])
    elif c in 'EWNS':
        m.move(c)
    else:
        assert(c in '^$')
        if c == '$':
            m.finalize()
            break
    if DEBUG:
        print(m, end='\n\n')
print(m, end='\n\n')

# ------------------------------------------------
# part 1
# ------------------------------------------------
print(np.max(m.d))

# ------------------------------------------------
# part 2
# ------------------------------------------------
print(len(list(zip(*np.where(m.d >= 1000)))))

# vim:sts=4:sw=4:et:
