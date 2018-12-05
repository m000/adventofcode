#!/usr/bin/env python3
import sys
from pprint import pprint
INPUT = 'd05-input.txt'

# ------------------------------------------------

def process(stack, chars):
    for cn, c in enumerate(chars):
        #print(c, stack) # slow
        stack.append(c)

        if (len(stack) < 2):
            continue
        v0 = stack.pop()
        v1 = stack.pop()
        cv0 = v0.casefold()
        cv1 = v1.casefold()

        if cv0 != cv1:
            stack.append(v1)
            stack.append(v0)
            continue
        elif v0 == v1:
            stack.append(v1)
            stack.append(v0)
            continue
        else:
            continue

# ------------------------------------------------

# part 1
stack = []
with open(INPUT) as f:
    for ln, line in enumerate(f):
        line = line.strip()
        process(stack, line)
print(len(stack))

# ------------------------------------------------

# part 2
test_chars = set(''.join(stack).casefold())
test_results = {}
for c in sorted(test_chars):
    test_stack = []
    test_input = [ sc for sc in stack if sc.casefold() != c.casefold() ]
    process(test_stack, test_input)
    #print(c, len(test_stack), test_stack)
    test_results[c] = test_stack
bestc = min(test_results, key=lambda key: len(test_results[key]))
print(len(test_results[bestc]))

# vim:sts=4:sw=4:et:
