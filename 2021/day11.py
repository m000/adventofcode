#!/usr/bin/env python3.10

import logging
from collections import namedtuple
from itertools import chain

import numpy as np
from termcolor import colored

import aoc

Neighbours = namedtuple('Neighbours', ('n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'))


def datafmt(data):
    cdata = data.astype(str)
    cdata[data == 0] = colored('0', 'white', attrs=['bold'])
    return '\n'.join([''.join(row) for row in cdata])


def neighbours(i, j, data=None):
    all_neighbours = [
        (i - 1, j), (i - 1, j + 1), (i, j + 1), (i + 1, j + 1),
        #  n             ne            e            se
        (i + 1, j), (i + 1, j - 1), (i, j - 1), (i - 1, j - 1),
        #  s             sw            w            nw
    ]
    return Neighbours(*map(
        lambda n: n if n[0] >= 0 and n[1] >= 0 and n[0] < data.shape[0] and n[1] < data.shape[1] else None,
        all_neighbours
    ))


if __name__ == '__main__':
    aoc.logging_setup()
    data = np.genfromtxt(
        aoc.input_file(11),
        dtype=int, delimiter=1,  # delimiter = 1 -> fields of width 1
    )
    if not ((data >= 0).all() and (data < 9).all()):
        logging.error("Invalid input energy levels.")
        raise RuntimeError("Invalid input energy levels.")

    niter = 1
    nflashes_100 = 0
    iter_flash_all = -1
    while niter < 100 or iter_flash_all == -1:
        # flashed array marks octopuses flashed during this step
        flashed = np.zeros(data.shape, dtype=bool)
        data += 1
        while True:
            # flashed_new array marks octopuses that flashed during the last sub-step
            flashed_new = (data == 10) ^ (flashed)

            # if the sub-step didn't flash any octopuses, stop and proceed to next step
            if not flashed_new.any():
                break

            # update flashed, so flashed_new is correctly calculated in the next sub-step
            flashed |= flashed_new

            # visit the neighbours of all flashed octopuses and bump them up
            fcoords = set(zip(*map(list, np.where(flashed_new))))
            for n in chain(*[neighbours(*coords, data) for coords in fcoords]):
                if n is None or data[n] == 10:
                    continue
                data[n] += 1

        nflashed_step = np.sum(flashed)
        if niter < 100:
            nflashes_100 += nflashed_step
        if iter_flash_all == -1 and nflashed_step == data.size:
            iter_flash_all = niter
        data[flashed] = 0
        logging.debug(f'\n{datafmt(data)}\n')
        niter += 1

    # first part
    print(nflashes_100)

    # second part
    print(iter_flash_all)
