#!/usr/bin/env python3.10

from collections import Counter
from functools import reduce
from itertools import islice

import aoc

if __name__ == '__main__':
    lines = aoc.input_lines(3)
    ncolumns = len(lines[0])

    # first part
    columns = list(zip(*lines))
    gamma_rate_bits = [Counter(c).most_common()[0][0] for c in columns]
    epsilon_rate_bits = [Counter(c).most_common()[-1][0] for c in columns]
    bits2int = lambda ba: int(''.join(ba), base=2)
    print(bits2int(gamma_rate_bits) * bits2int(epsilon_rate_bits))

    # second part
    o2_lines, o2_rating = list(lines), None
    for i in range(ncolumns):
        columns = list(zip(*o2_lines))
        bitcounts = Counter(columns[i])
        filter_bit = max(bitcounts.items(), key=lambda t: (t[1], t[0]))[0]
        o2_lines = list(filter(lambda l: l[i] == filter_bit, o2_lines))
        if len(o2_lines) == 1:
            o2_rating = int(o2_lines[0], base=2)
            break
    if o2_rating is None:
        raise RuntimeError("Could not determine O2 rating.")

    co2_lines, co2_rating = list(lines), None
    for i in range(ncolumns):
        columns = list(zip(*co2_lines))
        bitcounts = Counter(columns[i])
        filter_bit = min(bitcounts.items(), key=lambda t: (t[1], t[0]))[0]
        co2_lines = list(filter(lambda l: l[i] == filter_bit, co2_lines))
        if len(co2_lines) == 1:
            co2_rating = int(co2_lines[0], base=2)
            break
    if co2_rating is None:
        raise RuntimeError("Could not determine CO2 rating.")

    print(o2_rating * co2_rating)
   
        

