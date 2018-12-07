#!/usr/bin/env python3
import sys
import re
import copy
from pprint import pprint

DEBUG = False
INPUT = 'd07-input.txt'
line_re = re.compile('Step (?P<s1>[a-zA-Z]+) must be finished (?P<when>[a-z]+) step (?P<s2>[a-zA-Z]+) can begin.')
duration = lambda s: 60 + ord(s) - ord('A') + 1

# ------------------------------------------------
# executes the steps with the provided config
# ------------------------------------------------
def work(steps, dependencies, nworkers):
    steps = steps.copy()
    dependencies = copy.deepcopy(dependencies)
    workers = [-1,] * nworkers              # when the worker is next available
    ongoing = [None,] * nworkers            # what the worker is working on
    order = []
    t = -1
    updated = True

    while not (not steps and ongoing.count(None) == nworkers):
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
        for i in range(nworkers):
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
        workers_available = [i for i in range(nworkers) if ongoing[i] is None and workers[i] <= t]
        steps_available = [s for s in sorted(steps) if s not in dependencies]
        for w, s in zip(workers_available, steps_available):
            updated = True
            workers[w] = t + duration(s)
            ongoing[w] = s
            order.append(s)
            steps.remove(s)

    return((''.join(order), t))

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

# ------------------------------------------------
# part 1
# ------------------------------------------------
print(work(steps, dependencies, 1))

# ------------------------------------------------
# part 2
# ------------------------------------------------
print(work(steps, dependencies, 5))

# vim:sts=4:sw=4:et:
