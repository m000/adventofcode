#!/usr/bin/env python3
import re
import sys
from pprint import pprint
INPUT = 'd12-input.txt'

DEBUG = False
if DEBUG:
    INPUT = 'd12-input-example.txt'

# read a rule from input
rule_re = re.compile(r'(?P<pattern>[.#]+)\s*=>\s*(?P<out>[.#])\s*')

# normalize/denormalize rules - avoid '.' to simplify using regex
norm = lambda s: s.replace('.', '_')
denorm = lambda s: s.replace('_', '.')

# max pattern length
max_plen = None

# ------------------------------------------------
# helpers
# ------------------------------------------------
def step(stuple, rules):
    s, o = stuple                   # initial state and offset
    slack = max_plen - 1            # slack to add at start/end of state
    s = '_'*slack + s + '_'*slack   # add the slack
    o -= slack                      # adjust starting offset
    snew = ['_',]*len(s)            # new state - start with no plants

    i = 0                           # position in string
    nextmatch = [-1,] * len(rules)  # position of next match for rules
    if DEBUG:
        print(s)
    while i < len(s):
        ss = s[i:]                  # substate we work on
        for ri, r in enumerate(rules):
            # search for next match
            if nextmatch[ri] is None or i < nextmatch[ri]:
                continue
            m = r[1].search(ss)
            if m is None:
                nextmatch[ri] = None
                continue

            # update
            mspan = m.span()
            nextmatch[ri] = mspan[0] + i + 1
            snew[i + (mspan[0] + mspan[1])//2] = r[2]

            if DEBUG:
                print(ri, r[0], m)
                print(''.join(snew))
        i += 1

    # trim empty pots and adjust starting offset
    snew = ''.join(snew)
    o += snew.find('#')
    snew = snew.strip('_')

    return((snew, o))

# ------------------------------------------------
# read initial state and rules
# ------------------------------------------------
init_state = None
rules = []
with open(INPUT) as f:
    for ln, line in enumerate(f):
        if line.startswith('initial state:'):
            if init_state is None:
                init_state = norm(line.split(':')[1].strip())
            else:
                print('Skipping initialization line %d: %s' % (ln, line.strip()), file=sys.stderr)
        else:
            m = rule_re.match(line)
            if m is None: continue
            assert(len(m['pattern']) % 2 != 0)  # pattern length must be odd
            p, o = norm(m['pattern']), norm(m['out'])
            rules.append((p, re.compile(p), o))
max_plen = max([len(r[0]) for r in rules])

# ------------------------------------------------
# part 1
# ------------------------------------------------
n = 20
state = init_state
state_offset = 0
print(state)
for i in range(n):
    state, state_offset = step((state, state_offset), rules)
print(state)
print(sum([i for i, p in enumerate(state, state_offset) if p == '#']))
print('')

# ------------------------------------------------
# part 2
# ------------------------------------------------
# For this problem to be feasible, we expect the state to either be
# periodic (with the specific set of rules) or converge to a stable
# state. We start with a simple loop checking for convergence.
# This worked!
n = 50000000000
state = init_state
state_offset = 0
print(state)

# look for a converged state
for i in range(n):
    prev_state = state
    prev_state_offset = state_offset
    state, state_offset = step((state, state_offset), rules)
    if (state == prev_state):
        break

# state converged! (offsets may still be different)
assert(i < n)
print(state)

# compute two consecutive sums to account for offset shift
sum0 = sum([i for i, p in enumerate(state, state_offset) if p == '#'])
state, state_offset = step((state, state_offset), rules)
sum1 = sum([i for i, p in enumerate(state, state_offset) if p == '#'])

# calculate the real sum at n
print('state converged at generation %d' % (i))
print(sum0 + (n-i-1)*(sum1-sum0))
print('')

# vim:sts=4:sw=4:et:
