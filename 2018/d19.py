#!/usr/bin/env python3
import re
import sys
import sympy
from sympy.utilities.lambdify import lambdify
from pprint import pprint
INPUT = 'd19-input.txt'
DEBUG = False

class AoCVM:
    def __init__(self, opcode_specfile=None, nregs=4):
        self.nregs = nregs
        self.regs = [0,] * self.nregs
        self.ip = None
        self.program = []
        self.opt = {}
        self.opcodes = {}
        self.ops = ['addr', 'addi', 'mulr', 'muli',
                'banr', 'bani', 'borr', 'bori', 'setr', 'seti',
                'gtir', 'gtri', 'gtrr', 'eqir', 'eqri', 'eqrr']
        self.opsmeta = { 'addr': ('+', 'rrr'), 'addi': ('+', 'rir'),
                'mulr': ('*', 'rrr'), 'muli': ('*', 'rir'),
                'banr': ('&', 'rrr'), 'bani': ('&', 'rir'),
                'borr': ('|', 'rrr'), 'bori': ('|', 'rir'),
                'setr': ('=', 'rir'), 'seti': ('=', 'iir'),
                'gtir': ('>', 'irr'), 'gtri': ('>', 'rir'), 'gtrr': ('>', 'rrr'),
                'eqir': ('==', 'irr'), 'eqri': ('==', 'rir'), 'eqrr': ('==', 'rrr') }
        if opcode_specfile is not None:
            self.samples_nmatch_hist = {}    # for part 1
            self.get_opcodes(opcode_specfile)

    def execute(self, infile=None, optimize=False):
        if infile is not None: self.load(infile)

        if self.ip is None:             # day 16
            for f, args in self.program:
                f(*args)
        elif not optimize:              # day 19
            while self.regs[self.ip] < len(self.program):
                f, args = self.program[self.regs[self.ip]]
                f(*args)
                self.regs[self.ip] += 1
        else:                           # day 19
            while self.regs[self.ip] < len(self.program):
                ip = self.regs[self.ip]
                if ip not in self.opt:
                    l = self.optimize(ip)
                else:
                    l = self.opt[ip]
                    self.regs = l(*self.regs)
                
    def ins2sympy(self, ins, sreg_array='sregv'):
        # construct symbolic arguments
        op, args = ins
        symop, argt = self.opsmeta[op.__name__]
        symargs = [ '%d' % a if t == 'i' else '%s[%d]' % (sreg_array, a) 
            for a, t in zip(args, argt)]
        # construct symbolic statement
        if op.__name__.startswith('set'):
            return '{2:s} {3:s} {0:s}'.format(*symargs, symop)
        elif symop == '==':
            return '{2:s} = sympy.Eq({0:s}, {1:s})'.format(*symargs, symop)
        else:
            return '{2:s} = {0:s} {3:s} {1:s}'.format(*symargs, symop)

    def optimize(self, ip):             # day 19
        # symbolic registers
        sreg = sympy.symbols(', '.join(['r[%d]' % n for n in range(self.nregs)]))

        # values of symbolic regs
        sregv = list(sreg)

        ip_start = ip
        bbl = 0

        while True:
            # create symbolic representation of instruction
            op, args = self.program[ip]
            s = self.ins2sympy((op, args), 'sregv')
            bbl += 1

            if DEBUG:
                print('%s %s' % (op.__name__, args))
                print(s)

            # execute symbolic representation of op
            exec(s)

            # increment symbolic ip
            sregv[self.ip] += 1

            # increment optimizer ip & continue
            if args[2] != self.ip:
                ip += 1
                continue

            # ip was written to - attempt chaining
            # covers cases we have observed in the input
            if op.__name__ == 'seti':
                ip = args[0] + 1
                continue
            elif op.__name__ == 'addi' and args[0] == self.ip:
                ip += args[1] + 1
                continue
            else:
                print('brk')
                #if DEBUG:
                print('%s %s' % (op.__name__, args))
                sregv = [sympy.expand(sr) for sr in sregv]
                print(sregv)
                print(10*'-')
                break

        self.opt[ip_start] = lambdify(sreg, sregv, ('math'))
        return self.opt[ip_start]

    def load(self, infile):
        self.program = []
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
                elif line.startswith('#ip'):
                    self.ip = int(line.split()[1])
                    continue

                line = line.split()
                op, args = (line[0], list(map(int, line[1:])))
                if op.isdigit():
                    op = self.opcodes[int(op)]
                op = getattr(self, op)
                self.program.append((op, args))

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
                for op in self.ops:
                    self.regs = before.copy()
                    f = getattr(self, op)
                    f(*ins[1:])
                    if (self.regs == after):
                        nmatches += 1
                        opcodes_match[ins[0]].add(op)
                        if DEBUG:
                            print('%s%s: %s -> %s' % (op, tuple(ins[1:]), before, after))
                    else:
                        opcodes_nomatch[ins[0]].add(op)
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
            for uopc, uop in self.unambiguous_opcodes().items():
                for aopc, ains in self.ambiguous_opcodes().items():
                    if uop in ains:
                        ains.remove(uop)
                        if len(ains) == 1:
                            self.opcodes[aopc] = self.opcodes[aopc].pop()
                            break_loop = False
            if break_loop: break
        return (len(self.unambiguous_opcodes()) == 0)

    def ambiguous_opcodes(self):
        return {opc: op for opc, op in self.opcodes.items() if type(op) is set and len(op) > 1}

    def unambiguous_opcodes(self):
        return {opc: op for opc, op in self.opcodes.items() if type(op) is not set}

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

if __name__ == '__main__':
    # ------------------------------------------------
    # part 1
    # ------------------------------------------------
    #vm = AoCVM(INPUT, nregs=6)
    #vm.load(INPUT)
    #vm.execute()
    #print(vm.regs)

    vm = AoCVM(INPUT, nregs=6)
    vm.load(INPUT)
    vm.regs[0] = 1
    vm.execute(optimize=True)
    print(vm.regs)

    # ------------------------------------------------
    # part 2
    # ------------------------------------------------
    #vm = AoCVM(INPUT, nregs=6)
    #vm.load(INPUT)
    #vm.optimize()

# vim:sts=4:sw=4:et:
