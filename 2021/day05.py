#!/usr/bin/env python3.10

import logging

import numpy as np

import aoc


def parse_input(specifier=None, only_hv=True):
    scanmap = np.zeros((1, 1), dtype=int)
    for n, ln in enumerate(aoc.input(5, specifier)):
        if ln == '':
            continue
        start, end = ln.split('->', maxsplit=1)
        # inverse x, y to produce same output as aoc example
        y0, x0 = list(map(int, start.split(',')))
        y1, x1 = list(map(int, end.split(',')))

        # first part - only process horizontal/vertical lines
        if not (x0 == x1 or y0 == y1):
            if only_hv:
                logging.debug(f"Skipping line {n}: {ln}")
                continue
            elif abs(x0 - x1) != abs(y0 - y1):
                raise ValueError(f"Line {n} is not a 45deg line: {ln}")

        # resize scanmap to fit data
        shape = max(x0 + 1, x1 + 1, scanmap.shape[0]), max(y0 + 1, y1 + 1, scanmap.shape[1])
        if shape != scanmap.shape:
            logging.debug(f'Resizing scanmap: {scanmap.shape} -> {shape}')
            scanmap_ = np.zeros(shape, dtype=int)
            scanmap_[0:scanmap.shape[0], 0:scanmap.shape[1]] = scanmap
            scanmap = scanmap_

        if x0 == x1:
            y = sorted([y0, y1])
            scanmap[x0, y[0]:y[1] + 1] += 1
        elif y0 == y1:
            x = sorted([x0, x1])
            scanmap[x[0]:x[1] + 1, y0] += 1
        else:
            # create an increment array for the diagonal line
            a = np.zeros((abs(x0 - x1) + 1, abs(y0 - y1) + 1), dtype=int)
            np.fill_diagonal(a, 1)
            if a.shape[0] != a.shape[1]:
                # this should never happen
                raise RuntimeError("WTF just happened?")

            # flip increment array to match the direction of the line
            if x0 > x1:
                a = np.flipud(a)
            if y0 > y1:
                a = np.fliplr(a)

            # add increment array to scanmap
            x, y = min(x0, x1), min(y0, y1)
            scanmap[x:x + a.shape[0], y:y + a.shape[1]] += a
        logging.debug(f'Scanmap after line {n}:\n{scanmap}\n')

    return scanmap


if __name__ == '__main__':
    # first part
    print(np.sum(parse_input() > 1))

    # second part
    print(np.sum(parse_input(only_hv=False) > 1))
