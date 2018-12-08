#!/usr/bin/env python3
import sys
import numpy
from pprint import pprint, pformat
INPUT = 'd08-input.txt'

# ------------------------------------------------
class NumStream:
    ''' Produces a stream of numbers from a file.
        Supports multi-line files.
    '''
    def __init__(self, filename):
        self.f = open(filename)
        self.n = map(int, self.f.readline().split())

    def __del__(self):
        if self.f is not None:
            self.f.close()
        self.f = None
        self.n = None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.n)
        except StopIteration as e:
            self.n = map(int, self.f.readline().split())
            return next(self.n)

class TreeNode:
    ''' Represents a tree node.
    '''
    def __init__(self, numstream):
        ''' Construct a tree node from the number stream.
        '''
        self.nchildren = next(numstream)
        self.nmeta = next(numstream)
        self.children = [TreeNode(numstream) for i in range(self.nchildren)]
        self.meta = [next(numstream) for i in range(self.nmeta)]

    def __repr__(self):
        return '<%s: %d children, %d meta, sum=%d, value=%d>' % (
                self.__class__.__name__,
                len(self.children),
                len(self.meta),
                self.sum(),
                self.value()
                )

    def sum(self):
        return sum(self.meta) + sum([c.sum() for c in self.children])

    def value(self):
        if self.children:
            return sum([ self.children[m-1].value()
                for m in self.meta
                if m <= len(self.children) and m > 0
                ])
        else:
            return sum(self.meta)
# ------------------------------------------------
# part 1 and 2
print(TreeNode(NumStream(INPUT)))

# vim:sts=4:sw=4:et:
