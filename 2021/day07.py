#!/usr/bin/env python3.10

from collections import Counter

import aoc


def part1(line):
    crabs = sorted([(pos, count) for pos, count in Counter(map(lambda s: int(s.strip()), line.split(','))).items()])
    fsum1 = lambda x: sum([count * abs(pos - x) for pos, count in crabs])
    print(min([fsum1(x) for x in range(crabs[0][0], crabs[-1][0])]))


def part2(line):
    crabs = sorted([(pos, count) for pos, count in Counter(map(lambda s: int(s.strip()), line.split(','))).items()])
    consumption = [0, ] * (crabs[-1][0] - crabs[0][0] + 1)
    for i in range(1, len(consumption)):
        consumption[i] = consumption[i - 1] + i
    fsum2 = lambda x: sum([count * consumption[abs(pos - x)] for pos, count in crabs])
    print(min([fsum2(x) for x in range(crabs[0][0], crabs[-1][0])]))


if __name__ == '__main__':
    # set loglevel and read input
    aoc.logging_setup()
    lines = aoc.input_lines(7)

    # first part
    part1(lines[0])

    # second part
    part2(lines[0])
