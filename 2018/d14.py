#!/usr/bin/env python3
import sys
import re

INPUT = 'd14-input.txt'
DEBUG = False

# ------------------------------------------------
# Helpers doing the work
# ------------------------------------------------
def digits(n):
    d = []
    while (n >= 10):
        d.append(n % 10)
        n //= 10
    d.append(n)
    d.reverse()
    return d

def p(scores, elves):
    print(' '.join(map(str, scores)))
    pe = [' ',] * len(scores)
    for i, e in enumerate(elves):
        pe[e] = str(i)
    print(' '.join(pe))
    print(80*'-')

def step(scores, elves):
    ext = digits(sum([scores[e % len(scores)] for e in elves]))
    scores.extend(ext)
    elves = [(e + scores[e] + 1) % len(scores) for e in elves]
    if DEBUG:
        print(ext)
        p(scores, elves)
    return (scores, elves, len(ext))

def run1(scores, elves, seed):
    while len(scores) < seed + 10:
        scores, elves, ext_len = step(scores, elves)
    return (scores, elves)

def run2(scores, elves, seed):
    seed_digits = digits(seed)
    seed_digits_len = len(seed_digits)

    while len(scores) < seed_digits_len:
        scores, elves, ext_len = step(scores, elves)

    not_done = True
    while not_done:
        # Scores may be extended for ext_len > 1.
        # We need to search for the seed in multiple positions.
        for i in range(ext_len):
            t = scores[-(seed_digits_len + i):][:seed_digits_len]
            if t == seed_digits:
                not_done = False
                scores = scores[:-i]
                break
        if not_done:
            scores, elves, ext_len = step(scores, elves)

    return (scores, elves)

# ------------------------------------------------
# Read input
# ------------------------------------------------
with open(INPUT) as f:
    seed = int(f.readline())
if DEBUG:
    seed = 2018

# ------------------------------------------------
# part 1
# ------------------------------------------------
scores = [3, 7]
elves = [0, 1]
scores, elves = run1(scores, elves, seed)
if DEBUG:
    p(scores, elves)
print(seed, ''.join(map(str, scores[seed:seed+10])))

# ------------------------------------------------
# part 2
# ------------------------------------------------
scores = [3, 7]
elves = [0, 1]
scores, elves = run2(scores, elves, seed)
if DEBUG:
    p(scores, elves)
print(seed, len(scores)-len(digits(seed)))

# vim:sts=4:sw=4:et:
