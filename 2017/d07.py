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
        self.tweight = None

    def __str__(self):
        return '%s (%d) -> %s' % (self.name, self.weight, self.children)

    def __repr__(self):
        return self.__str__()

    def get_tree_weight(self, progs):
        if self.tweight is None:
            w = self.weight
            for c in self.children:
                w += progs[c].get_tree_weight(progs)
            self.tweight = w
        return self.tweight

    def get_unbalanced(self, progs):
        if not self.children: return None

        # get weights and count them
        weights = {}
        for c in self.children:
            w = progs[c].get_tree_weight(progs)
            if not w in weights:
                weights[w] = []
            weights[w].append(c)

        # expect at most two different weights
        assert len(weights) < 3, 'More than one children unbalanced for %s.' % self.name

        weights = list(weights.items())
        if len(weights) == 1:
            # children balanced - return None
            return None
        elif len(weights[0][1]) == 1:
            # first tree weight unbalanced - return child name and adjustment
            return (weights[0][1][0], weights[1][0]-weights[0][0])
        elif len(weights[1][1]) == 1:
            # second tree weight unbalanced - return child name and adjustment
            return (weights[1][1][0], weights[0][0]-weights[1][0])
        else:
            assert False, 'WTF?'


# part 1 - read input
progs = {}
with open(INPUT) as f:
    for l in f:
        p = Node(l)
        progs[p.name] = p

# part 1 - loop and remove leaves
while len(progs) > 1:
    leaves = set(filter(lambda n: len(progs[n].children) == 0, progs))
    for l in leaves:
        del progs[l]
    for p in progs:
        progs[p].children = progs[p].children - leaves
root = list(progs.keys())[0]
print(root)

# part 2 - read input (again)
with open(INPUT) as f:
    for l in f:
        p = Node(l)
        progs[p.name] = p

# part 2 - traverse from root, following unbalanced
# the first node we find that has balanced children, has to be adjusted
prv = None
cur = progs[root].get_unbalanced(progs)
while cur is not None:
    #print(progs[cur[0]])
    prv = cur
    cur = progs[cur[0]].get_unbalanced(progs)
print(prv[0], progs[prv[0]].weight+prv[1])

# vim:sts=4:sw=4:et:
