#!/usr/bin/env python3
import re
import sys
import sympy
from sympy.utilities.lambdify import lambdify
from pprint import pprint
INPUT = 'd19-input.txt'
DEBUG = True

class AoCVM:
    def __init__(self, opcode_specfile=None, nregs=4):
        self.nregs = nregs              # number of registers
        self.regs = [0,] * self.nregs   # register array
        self.ip = None                  # index of the ip register
        self.count = 0                  # number of instructions executed
        self.program = []               # the loaded program
        self.opt = {}                   # optimization cache - day 19
        self.opcodes = {}               # map of opcodes to ops - day 16
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
            # day 16 - part 1
            self.samples_nmatch_hist = {}
            self.get_opcodes(opcode_specfile)
                
    def ins2sym(self, ins, prefix='sregv', sympy=True, as_array=True, replace_ip=False):
        ''' Converts an instruction to its symbolic form.
            When `as_array` is set, registers are printed as array members.
            When `replace_ip` is set, the ip register is printed as ip.
            When `sympy` is set, ops are printed for sympy evaluation.
        '''
        op, args = ins                                  # op function/arg numbers
        symop, symarg_type = self.opsmeta[op.__name__]  # op string/arg types

        # function converting arg number to symbolic form
        if as_array:
            mksymarg_0 = lambda a, t: '%d' % a if t == 'i' else '%s[%d]' % (prefix, a)
        else:
            mksymarg_0 = lambda a, t: '%d' % a if t == 'i' else '%s%d' % (prefix, a)

        # function replacing the ip register with ip
        if replace_ip:
            mksymarg = lambda a, t: 'ip' if t == 'r' and a == self.ip else mksymarg_0(a, t)
        else:
            mksymarg = mksymarg_0

        # change all args to symbolic names based on their type
        symargs = [ mksymarg(a, t) for a, t in zip(args, symarg_type) ]

        # construct symbolic statement
        if op.__name__.startswith('set'):
            return '{2:s} {3:s} {0:s}'.format(*symargs, symop)
        elif sympy and symop == '==':
            return '{2:s} = sympy.Eq({0:s}, {1:s})'.format(*symargs, symop)
        else:
            return '{2:s} = {0:s} {3:s} {1:s}'.format(*symargs, symop)

    def load(self, infile):
        ''' Loads a program from a file. Sample lines are ignored.
        '''
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

    def dump(self, infile=None):
        ''' Makes a static dump of program instructions.
        '''
        if infile is not None:
            self.load(infile)
        for n, ins in enumerate(self.program):
            print('%2d %s' % (n, self.ins2sym(ins, prefix='r',
                sympy=False, as_array=False, replace_ip=True)))

    def execute(self, infile=None, optimize=False):
        ''' Executes a program.
            If no register has been designated as ip, then the
            instructions are executed serially. The `optimize`
            flag is ignored.
            If a register has been designated as ip:
                - With the `optimize` flag off, the instructions
                are executed one by one. The ip register is
                incremented after each instruction.
                - With the `optimize` flag on, sympy is used to
                combine as many instruction as possible into a
                single lambda function which is cached.
                The lambda function is used to execute a block
                of instructions in a single step. The ip register
                is incremented at the end by the number of
                the original instructions.
        '''
        if infile is not None:
            self.load(infile)

        self.count = 0
        if self.ip is None:             # day 16
            for f, args in self.program:
                f(*args)
                self.count += 1
        elif not optimize:              # day 19
            while self.regs[self.ip] < len(self.program):
                f, args = self.program[self.regs[self.ip]]
                if DEBUG:
                    print(self.regs[self.ip], self.regs)
                    #print('%s %s' % (f.__name__, args))
                    print(self.ins2sym((f, args), 'r'))
                f(*args)
                self.regs[self.ip] += 1
                self.count += 1
                if DEBUG:
                    print(self.regs[self.ip], self.regs)
                    print('')
        else:                           # day 19
            while self.regs[self.ip] < len(self.program):
                ip = self.regs[self.ip]
                if ip not in self.opt:
                    l, bbl = self.optimize(ip)
                else:
                    l, bbl = self.opt[ip]
                    self.regs = l(*self.regs)
                self.count += bbl
                #print(ip, self.regs)
                #if ip == 11:
                    #print('X')
                    #sympy.solveset
                    #sys.exit(0)

    def optimize(self, ip):
        ''' Optimizes a series of instructions starting from ip to a
            single lambda function.
        '''
        # symbolic registers
        sreg = sympy.symbols(', '.join(['r[%d]' % n for n in range(self.nregs)]))

        # values of symbolic regs
        sregv = list(sreg)

        ip_start = ip
        bbl = 0

        while True:
            # create symbolic representation of instruction
            op, args = self.program[ip]
            s = self.ins2sym((op, args), 'sregv')
            bbl += 1

            if DEBUG:
                print('%s %s' % (op.__name__, args))
                print(s)

            # execute symbolic representation of op
            #print('-------')
            #print(s)
            #print(args[2], sregv)
            #print(sregv[3])
            exec(s)

            # convert bool to int
            #if op.__name__.startswith('eq') or op.__name__.startswith('gt'):
                #if sregv[args[2]] == sympy.true:
                    #sregv[args[2]] = 1
                #elif sregv[args[2]] == sympy.false:
                    #sregv[args[2]] = 0

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
                sregv = [sympy.expand(sr) for sr in sregv]
                ip_str = '{0:2d} {0:2d}'.format(ip_start, ip)
                print('B', ip_str, self.ins2sym((op, args), 'r'), file=sys.stderr)
                print('C', ip_str, sregv, file=sys.stderr)
                break

        self.opt[ip_start] = (lambdify(sreg, sregv, ('math')), bbl)
        return self.opt[ip_start]

    def get_opcodes(self, opcode_specfile):
        ''' Guesses the opcodes by example.
            Used for day 16.
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
        ''' Attempts to solve ambiguous opcode mappings.
            Used for day 16, part 2.
        '''
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
        ''' Returns the list of opcodes which are still ambiguous.
            Used for day 16, part 2.
        '''
        return {opc: op for opc, op in self.opcodes.items() if type(op) is set and len(op) > 1}

    def unambiguous_opcodes(self):
        ''' Returns the list of opcodes which are unambiguous.
            Used for day 16, part 2.
        '''
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
    vm = AoCVM(INPUT, nregs=6)
    vm.load(INPUT)
    vm.execute()
    print(vm.count, vm.regs)

    vm = AoCVM(INPUT, nregs=6)
    vm.load(INPUT)
    #vm.regs[0] = 1
    vm.execute(optimize=True)
    print(vm.count, vm.regs)

    # ------------------------------------------------
    # part 2
    # ------------------------------------------------
    #vm = AoCVM(INPUT, nregs=6)
    #vm.load(INPUT)
    #vm.optimize()

# vim:sts=4:sw=4:et:
