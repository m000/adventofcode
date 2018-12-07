#!/usr/bin/env python3
import sys
import re
import copy
from pprint import pprint

DEBUG = False
INPUT = 'd07-input.txt'
line_re = re.compile('Step (?P<s1>[a-zA-Z]+) must be finished (?P<when>[a-z]+) step (?P<s2>[a-zA-Z]+) can begin.')
NWORKERS = 5

# ------------------------------------------------
# scan input
# ------------------------------------------------
steps = set()
dependencies = {}
with open(INPUT) as f:
    for ln, line in enumerate(f):
        m = line_re.match(line.strip())
        if m is None:
            print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
            sys.exit(1)
        assert(m.group('when') == 'before')
        s1, s2 = (m.group('s1'), m.group('s2'))
        if s2 not in dependencies:
            dependencies[s2] = set()
        dependencies[s2].add(s1)
        steps.update((s1, s2))

# keep a copy of steps/deps for step 2
dependencies_c = copy.deepcopy(dependencies)
steps_c = steps.copy()

# ------------------------------------------------
# part 1
# ------------------------------------------------
nsteps = -1                             # guard against inf. loops
order = []                              # order of steps
while len(steps) > 0 and len(steps) != nsteps:
    nsteps = len(steps)
    next_step = set(sorted([s for s in steps if s not in dependencies or not dependencies[s]])[0])
    order.extend(next_step)            # update order
    steps -= next_step                 # update steps
    garbage = []
    for s, d in dependencies.items():  # update dependencies
        d -= next_step
        if not d:
            garbage.append(s)
    for s in garbage:                   # collect garbage
        dependencies.pop(s, None)
assert(not steps)
print(''.join(order))

# ------------------------------------------------
# part 2
# ------------------------------------------------
duration = lambda s: 60 + ord(s) - ord('A') + 1
steps = steps_c
dependencies = dependencies_c
workers = [-1,] * NWORKERS              # when the worker is next available
ongoing = [None,] * NWORKERS            # what the worker is working on
t = -1
updated = True

while not (not steps and ongoing.count(None) == NWORKERS):
    # increment clock
    t += 1

    # dump state
    if DEBUG and updated:
        print(t, file=sys.stderr)
        print(workers, file=sys.stderr)
        print(ongoing, file=sys.stderr)
        print(''.join(sorted(steps)), file=sys.stderr)
        print(''.join([s if s not in dependencies else '*' for s in sorted(steps)]), file=sys.stderr)
        print(dependencies, file=sys.stderr)
        print("", file=sys.stderr)
    updated = False

    # check workers for finished steps
    finished = set()
    for i in range(NWORKERS):
        if workers[i] <= t and ongoing[i] is not None:
            finished.add(ongoing[i])
            ongoing[i] = None

    # update dependencies to unblock steps
    if finished:
        updated = True
        unblocked = []
        for s, d in dependencies.items():   # update dependencies
            d -= finished
            if not d:
                unblocked.append(s)
        for s in unblocked:                 # collect garbage
            dependencies.pop(s, None)

    # assign available jobs
    workers_available = [i for i in range(NWORKERS) if ongoing[i] is None and workers[i] <= t]
    steps_available = [s for s in sorted(steps) if s not in dependencies]
    for w, s in zip(workers_available, steps_available):
        updated = True
        workers[w] = t + duration(s)
        ongoing[w] = s
        steps.remove(s)
print(t)

# vim:sts=4:sw=4:et:
