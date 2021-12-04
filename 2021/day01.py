#!/usr/bin/env python3.10

from collections import deque
from itertools import islice, pairwise

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


if __name__ == '__main__':
    # first part
    print(sum([b > a for a, b in pairwise(map(int, aoc.input_lines(1)))]))

    # second part
    print(sum([sum(b) > sum(a) for a, b in pairwise(sliding_window(map(int, aoc.input_lines(1)), 3))]))
