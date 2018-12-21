#!/usr/bin/env python3
import re
import sys
from pprint import pprint
from d19 import AoCVM
INPUT = 'd16-input.txt'
DEBUG = False

# ------------------------------------------------
# initialize
# ------------------------------------------------
vm = AoCVM(INPUT)

# ------------------------------------------------
# part 1
# ------------------------------------------------
print(sum([hv for n, hv in vm.samples_nmatch_hist.items() if n >= 3]))

# ------------------------------------------------
# part 2
# ------------------------------------------------
assert(len(vm.ambiguous_opcodes()) == 0)
vm.execute(INPUT)
print(vm.regs)

# vim:sts=4:sw=4:et:
