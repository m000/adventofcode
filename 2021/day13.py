#!/usr/bin/env python3.10

import logging
from itertools import repeat, takewhile

import numpy as np

import aoc

if __name__ == '__main__':
    aoc.logging_setup()
    inputf = aoc.input(13)

    # Convert bool array to string using unicode blocks.
    data2str = lambda data: '\n'.join([''.join(['█' if c else '·' for c in row]) for row in data])

    # Inverse x, y to produce same output as aoc example. Normalize dimensions to be odd.
    coords = list(map(lambda l: tuple(map(int, l.split(',')))[::-1], takewhile(lambda l: l != '', inputf)))
    normdim = lambda d: d + 2 if d % 2 else d + 1
    dimx, dimy = tuple(map(normdim, map(max, zip(*coords))))

    # Initialize data.
    data = np.zeros((dimx, dimy), dtype=bool)
    data.put(list(map(lambda c: c[0] * data.shape[1] + c[1], coords)), repeat(True))

    # Initialize folds.
    folds = list(
        map(lambda t: (t[0].strip(), int(t[1].strip())),
            map(lambda s: s.removeprefix('fold along').split('='),
                takewhile(lambda l: l.startswith('fold along'), inputf)))
    )
    logging.debug(f'initial\n{data2str(data)}\nfolds: {folds}')

    # Process folds.
    dots0 = 0
    for i, (axis, n) in enumerate(folds):
        if axis == 'y':
            data = data[:n, :].copy() | np.flipud(data[n + 1:, :])
            logging.debug(f'fold along {axis} on {n}\n{data2str(data)}')
        elif axis == 'x':
            data = data[:, :n].copy() | np.fliplr(data[:, n + 1:])
            logging.debug(f'fold along {axis} on {n}\n{data2str(data)}')
        else:
            raise ValueError("Invalid fold axis: {axis}")

        if i == 0:
            dots0 = np.sum(data)

    print(aoc.hr())

    # first part
    print(np.sum(data))

    # second part
    print(data2str(data))
