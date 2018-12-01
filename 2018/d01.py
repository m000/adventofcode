#!/usr/bin/env python3
from pprint import pprint
INPUT = 'd01-input.txt'

i = 0
s = 0
sum1 = 0
freqs = set()
calibr = None

while calibr is None:
    with open(INPUT) as f:
        for l in f:
            if calibr is None:
                if s in freqs:
                    calibr = s
                else:
                    freqs.add(s)
            c = int(l)
            #print('%d + %d -> %d' % (s, c, s+c))
            s += c
    if  i == 0:
        sum1 = s

print('%d %d' % (sum1, calibr))

# vim:sts=4:sw=4:et:
