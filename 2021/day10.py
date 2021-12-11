#!/usr/bin/env python3.10

import logging
from collections import namedtuple
from functools import reduce

from termcolor import colored

import aoc


def linefmt(line, invalid=[]):
    return ''.join([
        c if i not in invalid else colored(c, 'red') for i, c in enumerate(line)])


if __name__ == '__main__':
    aoc.logging_setup()

    pairs = {'(': ')', '{': '}', '[': ']', '<': '>'}
    pairs_inv = {v: k for k, v in pairs.items()}
    chars = set(pairs.keys()) | set(pairs_inv.keys())
    invalid_scores = {')': 3, ']': 57, '}': 1197, '>': 25137}
    incomplete_scores = {')': 1, ']': 2, '}': 3, '>': 4}

    # first part
    IncompleteLine = namedtuple('IncompleteLine', ['line', 'pending'])
    valid = []
    syntax_error_score = []
    for n, ln in enumerate(aoc.input(10), 1):
        pending_chunks = []
        invalid = []
        for i, c in enumerate(ln):
            if c not in chars:
                logging.error(f"Invalid character '{c}' in line {n}.")
            elif c in pairs:
                pending_chunks.append(c)
            elif pending_chunks[-1] == pairs_inv[c]:
                pending_chunks.pop()
            else:
                if not invalid:
                    syntax_error_score.append(invalid_scores[c])
                invalid.append(i)
        if not invalid:
            valid.append(IncompleteLine(ln, pending_chunks))
        logging.debug(linefmt(ln, invalid))

    # first part
    print(sum(syntax_error_score))

    # second part
    print(sorted(map(
        lambda t: reduce(lambda score, c: score * 5 + incomplete_scores[pairs[c]], reversed(t.pending), 0),
        valid
    ))[len(valid) // 2])
