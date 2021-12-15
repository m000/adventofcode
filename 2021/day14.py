#!/usr/bin/env python3.10

import logging
from collections import Counter, defaultdict, deque
from itertools import islice, pairwise, repeat, takewhile
from functools import cache

import numpy as np

import aoc


def part1(poly_template, rules, steps):
    poly = poly_template
    for i in range(steps):
        print(i)
        pnext = [poly[0]]
        for p in map(''.join, pairwise(poly)):
            pnext.extend([rules[p], p[1]])
        poly = pnext
    counts = Counter(poly).most_common()
    print(counts[0][1] - counts[-1][1])


def part2(poly_template, rules, steps, cache):
    print(poly_template)
    pass


if __name__ == '__main__':
    aoc.logging_setup()
    inputf = aoc.input(14)

    *_, poly_template = takewhile(lambda l: l != '', inputf)
    rules = dict(map(lambda s: map(str.strip, s.split('->')), takewhile(lambda l: l != '', inputf)))

    # first part
    part1(poly_template, rules, 10)
    part1(poly_template[:2], rules, 40)

    # second part
    cache = ()
    part2(poly_template, rules, 40, cache)

    import sys
    sys.exit(0)

#s_=sex
#pairs_=pairsex
#print(s_, Counter(s_))
#for i in range(5):
    #s_ = step(s_, pairs_)
    #print(len(s))
    #print(s_, Counter(s_))


#s_=sex[:2]
#pairs_=pairsex
#dp = {}
#for i in range(10):
    #s_ = step(s_, pairs_)
    #d = dict(Counter(s_))
    #print(5*'*' + ' ' + str(i))
    #for k in sorted(d.keys()):
        #kp = dp[k] if k in dp else 0
        #print(f'{k}: {kp:3d} -> {d[k]:3d} ({d[k] - kp})')
    #dp = d
    #print(s_, len(s_))
#print(len(s_))


#print(sex)
#pairs_=pairsex
#s0=sex[0]
#s1=sex[1]
#lol=set()
#c=Counter([s0, s1])
#for i in range(10):
    #pair = s0+s1
    #print(pair)
    #if pair in lol:
        #print('xxx')
        #break
    #lol.add(pair)
    #s1_ = pairs_[s0+s1]
    #c.update(s1_)
    #s1 = s1_
#print(pair)
#print(lol)
#print(s1)
#assert x == 3_298_534_883_329

#y=0
#for i in range(3_298_534_883_329):
    #y = 2*i - y
    #if (i % 1_000_000_000):
        #print(f'\r{(100*i)/3_298_534_883_329}', end='')
#print(y)
#x=2
#for i in range(40):
    #x+=(x-1)
#print(x)

#cache=defaultdict(dict)

#def nsteps(p, pairs, n):
    #s = p
    #for i in range(1, n+1):
        #if i in cache[s]:
            #return cache[s][i]
        #else:


    #s = poly[0]
    #for p in map(''.join, pairwise(poly)):
        #s += f'{pairs[p]}{p[1]}'
    #return s
