#!/usr/bin/env python3.10

import logging
from collections import Counter
from itertools import pairwise

import numpy as np

import aoc


def part1(line, niter):
    fish = np.fromstring(line, dtype=np.byte, sep=',')
    for i in range(1, niter + 1):
        need_reset = fish == 0
        fish -= 1
        fish[need_reset] = 6
        nbabies = np.sum(need_reset)
        if nbabies > 0:
            fish = np.append(fish, np.repeat(8, nbabies))
        logging.debug(f'{i:03d} {fish.shape[0]:3d} {fish}')
    print(fish.shape[0])


def part2(line, niter):
    # who needs numpy?
    fish = {n: 0 for n in range(0, 9)} | Counter(map(lambda s: int(s.strip()), line.split(',')))
    for i in range(1, niter + 1):
        nbabies = fish[0]
        for t0, t1 in pairwise(range(0, 9)):
            # loop "floats" fish[0] to fish[8]
            fish[t0], fish[t1] = fish[t1], fish[t0]
        if nbabies > 0:
            # reinstate the fish that had their cycle reset
            fish[6] += nbabies
        logging.debug(f'{i:03d} {sum(fish.values()):16d} {[fish[n] for n in range(0, 9)]}')
    print(sum(fish.values()))


if __name__ == '__main__':
    # set loglevel and read input
    aoc.logging_setup()
    lines = aoc.input_lines(6)

    # first part
    part1(lines[0], 80)

    # second part
    part2(lines[0], 256)
