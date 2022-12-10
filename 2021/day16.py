#!/usr/bin/env python3.10

from collections import deque
from itertools import islice, pairwise, chain
import logging

import aoc


class BITSPacket:
    TYPE_LITERAL = 4
    LENGTH_TYPE_BITS = 0
    LENGTH_TYPE_SUBPACKETS = 1

    def __init__(self, bit_input, level=0):
        self.bits = bit_input
        self.level = level
        self.nbits = 0
        self.subpackets = []
        self.version = self.read_int(3)
        self.type = self.read_int(3)
        logging.debug(f"{self.indent}Read packet header: version={self.version}, type={self.type}")

        if self.type == self.TYPE_LITERAL:
            self.value = self.read_literal()
            return

        elif self.read_int(1) == self.LENGTH_TYPE_BITS:
            subpackets_length = self.read_int(15)
            logging.debug(f"{self.indent}Reading subpackets up to {subpackets_length} bits.")
            while (nbits_sub := sum([p.nbits for p in self.subpackets])) < subpackets_length:
                self.subpackets.append(BITSPacket(self.bits, level=self.level + 1))
            if nbits_sub > subpackets_length:
                msg = f"{self.indent}Read more bits than expected: {nbits_sub} > {subpackets_length}."
                logging.error(msg)
                raise RuntimeError(msg)
            logging.debug(f"{self.indent}Read {len(self.subpackets)} subpackets in {nbits_sub} bits.")
        else:
            nsubpackets = self.read_int(11)
            for i in range(nsubpackets):
                self.subpackets.append(BITSPacket(self.bits, level=self.level + 1))

    @property
    def indent(self):
        return self.level * '    '

    def read(self, n=1):
        self.nbits += n
        return ''.join(islice(self.bits, n))

    def read_int(self, n=1):
        self.nbits += n
        return int(''.join(islice(self.bits, n)), 2)

    def read_literal(self):
        bits = []
        while (frag := self.read(5))[0] != '0':
            bits.append(frag[1:])
        bits.append(frag[1:])
        return int(''.join(bits), 2)

    def __repr__(self):
        return f'{self.__class__}'


if __name__ == '__main__':
    aoc.logging_setup()

    h2b = lambda c: f'{int(c, 16):04b}'
    bit_input = chain.from_iterable(map(h2b, aoc.char_input(16, valid=set('ABCDEF0123456789'), ignored='\n')))

    while True:
        bp = BITSPacket(bit_input)
        print(bp)

        #buf.append(b)
        #if 
        #print(b)

    # first part
    #print(sum([b > a for a, b in pairwise(map(int, aoc.input_lines(1)))]))

    # second part
    #print(sum([sum(b) > sum(a) for a, b in pairwise(sliding_window(map(int, aoc.input_lines(1)), 3))]))
