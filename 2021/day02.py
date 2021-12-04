#!/usr/bin/env python3.10

from collections import deque
from functools import reduce
from itertools import islice

import aoc


def sliding_window(iterable, n):
    # sliding_window('ABCDEFG', 4) -> ABCD BCDE CDEF DEFG
    it = iter(iterable)
    window = deque(islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for x in it:
        window.append(x)
        yield tuple(window)


def reduce_f1(coords, instruction_line):
    instr, n = instruction_line.split(maxsplit=1)
    if instr == 'forward':
        coords[0] += int(n)
    elif instr == 'up':
        coords[1] -= int(n)
    elif instr == 'down':
        coords[1] += int(n)
    else:
        raise ValueError(f'Bad instruction: {instr}.')
    return coords


def reduce_f2(coords, instruction_line):
    instr, n = instruction_line.split(maxsplit=1)
    if instr == 'forward':
        coords[0] += int(n)
        coords[1] += coords[2] * int(n)
    elif instr == 'up':
        coords[2] -= int(n)
    elif instr == 'down':
        coords[2] += int(n)
    else:
        raise ValueError(f'Bad instruction: {instr}.')
    return coords


if __name__ == '__main__':
    # first part
    end_coords = reduce(reduce_f1, aoc.input_lines(2), [0, 0])
    print(end_coords[0] * end_coords[1])

    # second part
    end_coords = reduce(reduce_f2, aoc.input_lines(2), [0, 0, 0])
    print(end_coords[0] * end_coords[1])
