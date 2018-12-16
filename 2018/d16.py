#!/usr/bin/env python3
import re
import sys
from pprint import pprint
INPUT = 'd16-input.txt'
DEBUG = False

# ------------------------------------------------
# helpers
# ------------------------------------------------
class AoCVM:
    def __init__(self, opcode_specfile=None, nregs=4):
        self.nregs = nregs
        self.regs = [0,] * self.nregs
        self.opcodes = {}
        self.instructions = ['addr', 'addi', 'mulr', 'muli',
                'banr', 'bani', 'borr', 'bori', 'setr', 'seti',
                'gtir', 'gtri', 'gtrr', 'eqir', 'eqri', 'eqrr']
        if opcode_specfile is not None:
            self.samples_nmatch_hist = {}    # for part 1
            self.get_opcodes(opcode_specfile)

    def execute(self, infile):
        l2ins = lambda l: list(map(int, l.split()))
        with open(infile) as f:
            lines = enumerate(f)
            for ln, line in lines:
                line = line.strip().lower()
                if line == '':
                    continue
                elif line.startswith('before:'):
                    next(lines)
                    next(lines)
                    continue

                ins = l2ins(line)
                ins_f = getattr(self, self.opcodes[ins[0]])
                ins_f(*ins[1:])

    def get_opcodes(self, opcode_specfile):
        ''' Guesses the opcodes by example.
        '''
        l2regs = lambda l: list(map(int, l[l.index('[')+1:l.index(']')].split(',')))
        l2ins = lambda l: list(map(int, l.split()))
        regs_bak = self.regs

        with open(opcode_specfile) as f:
            opcodes_match = {}
            opcodes_nomatch = {}
            lines = enumerate(f)
            for ln, line in lines:
                line = line.strip().lower()
                if not line.startswith('before:'): continue

                before = l2regs(line)
                ins = l2ins(next(lines)[1])
                after = l2regs(next(lines)[1])
                assert(len(before) == self.nregs)
                assert(len(ins) == 4)
                assert(len(after) == self.nregs)

                if ins[0] not in opcodes_match:
                    opcodes_match[ins[0]] = set()
                if ins[0] not in opcodes_nomatch:
                    opcodes_nomatch[ins[0]] = set()
                
                nmatches = 0
                for ins_name in self.instructions:
                    self.regs = before.copy()
                    ins_f = getattr(self, ins_name)
                    ins_f(*ins[1:])
                    if (self.regs == after):
                        nmatches += 1
                        opcodes_match[ins[0]].add(ins_name)
                        if DEBUG:
                            print('%s%s: %s -> %s' % (ins_name, tuple(ins[1:]), before, after))
                    else:
                        opcodes_nomatch[ins[0]].add(ins_name)
                if nmatches in self.samples_nmatch_hist:
                    self.samples_nmatch_hist[nmatches] += 1
                else:
                    self.samples_nmatch_hist[nmatches] = 1
                
            # initialize opcodes
            self.opcodes = {}
            for op in opcodes_match:
                opcodes = opcodes_match[op] - opcodes_nomatch[op]
                if len(opcodes) > 1:
                    self.opcodes[op] = opcodes
                else:
                    self.opcodes[op] = opcodes.pop()
            self.solve_opcodes()
        self.regs = regs_bak

    def solve_opcodes(self):
        while len(self.unambiguous_opcodes()) != 0:
            break_loop = True
            for uop, uins in self.unambiguous_opcodes().items():
                for aop, ains in self.ambiguous_opcodes().items():
                    if uins in ains:
                        ains.remove(uins)
                        if len(ains) == 1:
                            self.opcodes[aop] = self.opcodes[aop].pop()
                            break_loop = False
            if break_loop: break
        return (len(self.unambiguous_opcodes()) == 0)

    def ambiguous_opcodes(self):
        return {op: ins for op, ins in self.opcodes.items() if type(ins) is set and len(ins) > 1}

    def unambiguous_opcodes(self):
        return {op: ins for op, ins in self.opcodes.items() if type(ins) is not set}

    def addr(self, a, b, c):
        self.regs[c] = self.regs[a] + self.regs[b]

    def addi(self, a, b, c):
        self.regs[c] = self.regs[a] + b

    def mulr(self, a, b, c):
        self.regs[c] = self.regs[a] * self.regs[b]

    def muli(self, a, b, c):
        self.regs[c] = self.regs[a] * b

    def banr(self, a, b, c):
        self.regs[c] = self.regs[a] & self.regs[b]

    def bani(self, a, b, c):
        self.regs[c] = self.regs[a] & b

    def borr(self, a, b, c):
        self.regs[c] = self.regs[a] | self.regs[b]

    def bori(self, a, b, c):
        self.regs[c] = self.regs[a] | b

    def setr(self, a, b, c):
        self.regs[c] = self.regs[a]

    def seti(self, a, b, c):
        self.regs[c] = a

    def gtir(self, a, b, c):
        self.regs[c] = int(a > self.regs[b])

    def gtri(self, a, b, c):
        self.regs[c] = int(self.regs[a] > b)

    def gtrr(self, a, b, c):
        self.regs[c] = int(self.regs[a] > self.regs[b])

    def eqir(self, a, b, c):
        self.regs[c] = int(a == self.regs[b])

    def eqri(self, a, b, c):
        self.regs[c] = int(self.regs[a] == b)

    def eqrr(self, a, b, c):
        self.regs[c] = int(self.regs[a] == self.regs[b])

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
