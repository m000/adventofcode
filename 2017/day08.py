#!/usr/bin/env python3
import sys
from pathlib import Path as _P
import re

INPUT_DEFAULT = _P(__file__).with_name('%s-input.txt' % _P(__file__).stem)
INPUT = sys.argv[1] if len(sys.argv) > 1 else INPUT_DEFAULT

# wrapper class
class Ins:
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


# part 1 - read input
regs = {}
gmax = 0
with open(INPUT) as f:
    for l in f:
        reg, op, arg, _if, ifreg, ifcond, ifarg = l.split()
        assert op in ['inc', 'dec'], 'Invalid op: %s' % op
        assert ifcond in ['==', '!=', '<', '>', '<=', '>='], 'Invalid conditional: %s' % ifcond

        if reg not in regs:
            regs[reg] = 0
        if ifreg not in regs:
            regs[ifreg] = 0
        arg = int(arg) if op == 'inc' else -int(arg)
        ifarg = int(ifarg)

        print(reg, op, arg, _if, ifreg, ifcond, ifarg)
        if eval('%d %s %d' % (regs[ifreg], ifcond, ifarg)):
            regs[reg] += arg
            if regs[reg] > gmax: gmax = regs[reg]

print(max(regs.values()), gmax)
# vim:sts=4:sw=4:et:
