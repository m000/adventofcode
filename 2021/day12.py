#!/usr/bin/env python3.10

import logging
from collections import Counter, defaultdict
from copy import deepcopy
from functools import reduce

from termcolor import colored

import aoc


class Cave:
    def __init__(self, s):
        if self.is_invalid(s):
            raise ValueError(f"Invalid cave specification: {s}")

        self.name = s
        self.is_big = self.__class__.is_big(s)
        self.is_small = self.__class__.is_small(s)
        self.is_special = self.__class__.is_special(s)

    @classmethod
    def is_big(cls, s):
        return s.upper() == s

    @classmethod
    def is_small(cls, s):
        return s.lower() == s

    @classmethod
    def is_special(cls, s):
        return s in ('start', 'end')

    @classmethod
    def is_invalid(cls, s):
        return not (cls.is_big(s) or cls.is_small(s))

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self}>'

    def is_visitable_from(self, path):
        if self.is_big:
            return True
        else:
            return self.name not in path.walked


class Cave2(Cave):
    MAX_SMALL_CAVE_VISITS = 2

    def is_visitable_from(self, path):
        if self.is_big:
            return True
        elif self.is_special:
            return self.name not in path.walked
        else:
            walkcounts = Counter(filter(Cave2.is_small, path.walked))
            if max(walkcounts.values()) < 2:
                return True
            else:
                return walkcounts[self.name] < 1


class Path:
    def __init__(self, start, continuations, cavecls=Cave):
        if start not in continuations:
            raise ValueError(f"Starting path segment {start} not in continuations {continuations}.")
        self.walked = [start]
        self.continuations = deepcopy(continuations)
        cave_names = reduce(lambda a, b: a | b, self.continuations.values(), self.continuations.keys())
        self.caves = {c: cavecls(c) for c in cave_names}

    def pathstr(self):
        return colored('-', 'white', attrs=['bold']).join([colored(p, 'blue') for p in self.walked])

    def contstr(self):
        format_cont_set = lambda cont_set: ' '.join([f'{str(self.caves[c]):^7}' for c in cont_set])
        return '\n  '.join([
            f'{start:>5}: {format_cont_set(cont_set)}' if start != self.tail
            else colored(f'{start:>5}: {format_cont_set(cont_set)}', 'red')
            for start, cont_set in self.continuations.items()
        ])

    def __str__(self):
        if self.is_done():
            contstr = colored('DONE', 'green', attrs=['bold'])
        elif self.is_deadend():
            contstr = colored('DEADEND', 'red', attrs=['bold']) + "\n  " + self.contstr()
        else:
            contstr = self.contstr()
        return f'{self.pathstr()}\n  {contstr}\n'

    def cleanup(self, start=None):
        start = start if start is not None else self.tail
        remove_filter = lambda c: not self.caves[c].is_visitable_from(self)
        remove = set(filter(remove_filter, self.continuations[start]))
        self.continuations[start] -= remove

    @property
    def tail(self):
        return self.walked[-1]

    def is_done(self):
        return self.tail == 'end'

    def is_deadend(self):
        return not self.continuations[self.tail]

    def walk_to(self, cont, update_self=False):
        p = self if update_self else deepcopy(self)
        p.walked.append(cont)
        return p


def print_paths(pathlist, niter=None):
    print(aoc.hr(label=niter))
    print('\n'.join([f'{i}:{p}' for i, p in enumerate(pathlist)]))


def explore(continuations, cavecls):
    allpaths = [Path('start', continuations, cavecls=cavecls)]
    niter = 0
    continued = True
    while continued:
        continued = False
        niter += 1
        addedpaths = []
        for i, p in enumerate(allpaths):
            # Remove non-visitable caves from tail's continuations.
            p.cleanup()

            # Check if done or deadend.
            if p.is_done() or p.is_deadend():
                continue

            # Progress was made.
            continued = True

            # Extend paths.
            cont_list = list(p.continuations[p.tail])
            for cont in cont_list[1:]:
                addedpaths.append(p.walk_to(cont))

            # Modify current path. Has to be done last.
            p.walk_to(cont_list[0], update_self=True)
        allpaths.extend(addedpaths)
    return allpaths


if __name__ == '__main__':
    aoc.logging_setup()

    # Read input.
    continuations = defaultdict(set)
    for n, seg in aoc.input_enum(12):
        a, b = seg.split('-', 1)
        if Cave.is_invalid(a) or Cave.is_invalid(b):
            logging.error(f'Skipping invalid path segment {seg} on input line {n}.')
            continue
        continuations[a].add(b)
        continuations[b].add(a)

    # first part
    allpaths = explore(continuations, Cave)
    print(sum(map(lambda p: p.is_done(), allpaths)))

    # second part
    allpaths = explore(continuations, Cave2)
    print(sum(map(lambda p: p.is_done(), allpaths)))
