#!/usr/bin/env python3.10

import logging
from functools import reduce

import numpy as np
from termcolor import colored

import aoc


def datafmt(data, marked=[], highlighted=[]):
    cdata = data.astype(str)
    for coords in highlighted:
        cdata[coords] = colored(cdata[coords], 'yellow', attrs=['bold'])
    for coords in marked:
        if coords in highlighted:
            continue
        cdata[coords] = colored(cdata[coords], 'red')
    return '\n'.join([''.join(row) for row in cdata])


def neighbours(i, j, data=None):
    up, down, left, right = (i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)
    for c in (up, down, left, right):
        if data is None:
            yield c
        elif c[0] >= 0 and c[1] >= 0 and c[0] < data.shape[0] and c[1] < data.shape[1]:
            yield c
        else:
            continue


if __name__ == '__main__':
    aoc.logging_setup()
    data = np.genfromtxt(
        aoc.input_file(9),
        dtype=int, delimiter=1,  # delimiter = 1 -> fields of width 1
    )

    # first part
    low_points = []
    for i, j in np.ndindex(data.shape):
        neighbours_a = np.array(list(neighbours(i, j, data)))
        lowest = np.ndarray.min(data[tuple([*neighbours_a.T])])
        if data[i, j] < lowest:
            low_points.append((i, j))
    logging.debug(f'\n{datafmt(data, [], low_points)}')
    print(reduce(lambda a, b: a + data[b] + 1, low_points, 0))

    # second part
    basins = []
    for start in low_points:
        explored = {start}
        to_explore = list(filter(lambda n: data[n] < 9, neighbours(*start, data)))
        while to_explore:
            here = to_explore.pop()
            if here in explored:
                continue
            explored.add(here)
            v = data[here]
            for n in neighbours(*here, data):
                if data[n] < 9 and n not in explored:
                    to_explore.append(n)
        basins.append(explored)

    basins.sort(key=lambda s: len(s))
    logging.debug(f'\n{datafmt(data, reduce(set.union, basins), low_points)}')
    print(reduce(lambda a, b: a * len(b), basins[-3:], 1))
