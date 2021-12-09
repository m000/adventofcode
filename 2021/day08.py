#!/usr/bin/env python3.10
import logging
from collections import Counter

import aoc


def parse_input(specifier=None):
    signals = []
    output = []
    for ln in aoc.input(8, specifier=specifier):
        lsig, delim, lout = ln.partition('|')
        if delim == '' or output == '':
            logging.warning(f"Malformed input line: {ln}")
            continue
        lsig = [set(s.strip()) for s in lsig.split()]
        lout = [''.join(sorted(set(s.strip()))) for s in lout.split()]
        if (len(lsig) != 10 or len(lout) != 4):
            logging.warning(f"Malformed input line: {ln}")
            continue
        signals.append(lsig)
        output.append(lout)
    return signals, output


if __name__ == '__main__':
    aoc.logging_setup()
    signals, output = parse_input()
    output_digits = []
    output_numbers = []
    for sig, out in zip(signals, output):
        # filters to map digits to sets of signals - order is important
        sigset = {}
        segmap = {}

        # simplest of digit to signal set mappings
        sigset[1] = next(filter(lambda s: len(s) == 2, sig))  # 2 signals -> 1
        sigset[3] = next(filter(lambda s: len(s) == 5 and s.issuperset(sigset[1]), sig))  # 5 signals, contains 1 -> 3
        sigset[4] = next(filter(lambda s: len(s) == 4, sig))  # 4 signals -> 4
        sigset[7] = next(filter(lambda s: len(s) == 3, sig))  # 3 signals -> 7
        sigset[8] = next(filter(lambda s: len(s) == 7, sig))  # 4 signals -> 8

        # simplest of segment mappings
        segmap['a'] = (sigset[7] - sigset[1]).pop()
        segmap['b'] = (sigset[4] - sigset[3]).pop()
        segmap['g'] = (sigset[3] - sigset[4] - {segmap['a']}).pop()

        # more complex signal set mappings
        sigset[5] = next(filter(lambda s: len(s) == 5 and segmap['b'] in s, sig))
        sigset[6] = next(filter(lambda s: len(s) == 6 and s | sigset[1] == sigset[8], sig))

        # the rest of segment mappings
        segmap['c'] = (sigset[8] - sigset[6]).pop()
        segmap['f'] = (sigset[1] - {segmap['c']}).pop()
        segmap['d'] = (sigset[4] - {segmap['b'], segmap['c'], segmap['f']}).pop()
        segmap['e'] = (sigset[8] - set(segmap.values())).pop()

        # the rest of the signal set mappings
        sigset[0] = next(filter(lambda s: s == sigset[8] - {segmap['d']}, sig))
        sigset[2] = next(filter(lambda s: s == sigset[8] - {segmap['b'], segmap['f']}, sig))
        sigset[9] = next(filter(lambda s: s == sigset[8] - {segmap['e']}, sig))

        # calculate inverse set mapping
        sigset_inv = {''.join(sorted(s)): d for d, s in sigset.items()}

        if len(sigset) != 10:
            logging.error(f"Unable to decode signal line {sig}.")
            continue
        if len(sigset) != len(sigset_inv):
            logging.error(f"Decoded mapping for signal line {sig} is not 1-1.")
            continue
        if len(segmap) != 7:
            logging.error(f"Unable to produce segment map for signal line {sig}.")
            continue

        for d in out:
            output_digits.append(sigset_inv[d])
        output_numbers.append(sum([d * 10**i for i, d in enumerate(reversed(output_digits[-4:]))]))

    # first part
    output_digits_counts = Counter(output_digits)
    print(sum([output_digits_counts[d] for d in [1, 4, 7, 8]]))

    # second part
    print(sum(output_numbers))
