#!/usr/bin/env python3
import sys
from pathlib import Path as _P
import re

INPUT_DEFAULT = _P(__file__).with_name('%s-input.txt' % _P(__file__).stem)
INPUT = sys.argv[1] if len(sys.argv) > 1 else INPUT_DEFAULT

# wrapper class
class Node:
    def __init__(self, line):
        node, sep, children = l.partition('->')
        node_match = re.match(r'(?P<name>[a-z]+)\s+\((?P<weight>[0-9]+)\)\s*', node)
        if not node_match:
            raise Exception('Bad line: %s\n' % line)
        self.name = node_match.group('name')
        self.weight = int(node_match.group('weight'))
        self.children = set() if not children else set([c.strip() for c in children.split(',')])

    def __str__(self):
        return '%s (%d) -> %s' % (self.name, self.weight, self.children)

    def __repr__(self):
        return self.__str__()

# parse input
progs = {}
with open(INPUT) as f:
    for l in f:
        p = Node(l)
        progs[p.name] = p

# loop and remove leaves
while len(progs) > 1:
    leaves = set(filter(lambda n: len(progs[n].children) == 0, progs))
    for l in leaves:
        del progs[l]
    for p in progs:
        progs[p].children = progs[p].children - leaves

print(progs)


# vim:sts=4:sw=4:et:
