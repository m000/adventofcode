#!/usr/bin/env python3
import sys
import re
import itertools
import z3
from scipy.spatial import distance
from pprint import pprint

INPUTS = ['d23-input.txt', 'd23-input-example1.txt', 'd23-input-example2.txt']
DEBUG = False
INPUT = INPUTS[2] if DEBUG else INPUTS[0]

input_re = re.compile(r'pos=<([\d\s,-]+)>,\s*r=(\d+)')

# ------------------------------------------------
# read and label coords
# ------------------------------------------------
class NanoBot:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius

    def __lt__(self, other):
        return self.radius < other.radius

    def __str__(self):
        return '<pos=%s, radius=%d>' % (self.pos, self.radius)

    def __repr__(self):
        return str(self)

    def distance(self, other):
        if other.__class__ is NanoBot:
            return distance.cityblock(self.pos, other.pos)
        else:
            return distance.cityblock(self.pos, other)

    def in_range(self, other):
        return self.distance(other) <= self.radius

    @classmethod
    def weight_center(self, bots):
        return list(map(sum, zip(*[b.pos for b in bots])))

bots = []
with open(INPUT) as f:
    for ln, line in enumerate(f):
        m = input_re.match(line)
        if m is not None:
            pos = list(map(int, m.group(1).split(',')))
            r = int(m.group(2))
            bots.append(NanoBot(pos, r))
bots.sort()

# ------------------------------------------------
# part 1
# ------------------------------------------------
in_range = [bots[-1].in_range(b) for b in bots]
print(sum(in_range))
print('')

# ------------------------------------------------
# part 2
# ------------------------------------------------

zabs = lambda x: z3.If(x>=0, x, -x)
x, y, z = z3.Ints('x y z')

o = z3.Optimize()
in_range = []
in_range_count = z3.Int('in_range_count')
for i, b in enumerate(bots):
    in_range_f = z3.If(zabs(b.pos[0]-x) + zabs(b.pos[1]-y) + zabs(b.pos[2]-z) <= b.radius, 1, 0)
    in_range_var = z3.Int('in_range_%04d' % i)
    in_range.append(in_range_var)
    o.add(in_range_var == in_range_f)
o.add(in_range_count == sum(in_range))

h1 = o.maximize(in_range_count)
h2 = o.minimize(zabs(x) + zabs(y) + zabs(z))

print('Optimizing model...')
if o.check() == z3.sat:
    print('ok')
    m = o.model()
    print('x, y, z = %s' % ((m[x], m[y], m[z]),))
    print('distance: %s-%s' % (o.lower(h2), o.upper(h2)))
else:
    print('failed')

# vim:sts=4:sw=4:et:
