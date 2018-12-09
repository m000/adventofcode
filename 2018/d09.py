#!/usr/bin/env python3
import sys
import re
from pprint import pprint
from termcolor import colored
from progress.bar import IncrementalBar

INPUT = 'd09-input.txt'
DEBUG = False

# ------------------------------------------------
# Class modeling the game.
# ------------------------------------------------
class MarbleGame:
    mplain_fmt = lambda n: ' %d' % (n)
    mbold_fmt = lambda n: ' %s' % (colored(n, 'green'))
    round_fmt = lambda n: colored('[%3d]' % (n), 'red')

    score_multipleof = 23
    score_backsteps = 7

    def __init__(self, nplayers, last_marble):
        self.last_marble = last_marble
        self.score = [0,] * nplayers
        self.board = [0]
        self.current_marble = 1
        self.current_pos = 0
        self.current_round = 0
        if DEBUG:
            print(self)
        else:
            self.bar = IncrementalBar(max=self.last_marble)

    def __str__(self):
        s_round = MarbleGame.round_fmt(self.current_round)
        s_marbles = ''.join([
            MarbleGame.mbold_fmt(m) if i == self.current_pos else MarbleGame.mplain_fmt(m)
            for i, m in enumerate(self.board)
            ])
        return '%s%s' % (s_round, s_marbles)

    @property
    def scoring_player(self):
        if self.current_round > 0:
            return (self.current_round - 1) % len(self.score)
        else:
            return None

    def finished(self):
        return self.current_marble > self.last_marble

    def next_round(self):
        if self.finished():
            return None

        if self.current_marble % MarbleGame.score_multipleof != 0:
            self.current_pos = self.current_pos + 2
            if (self.current_pos > len(self.board)):
                self.current_pos -= len(self.board)
            self.board.insert(self.current_pos, self.current_marble)
            self.current_marble += 1
            self.current_round += 1
        else:
            # score current marble
            self.score[self.scoring_player] += self.current_marble

            # remove and score another marble
            remove_pos = (self.current_pos - MarbleGame.score_backsteps)
            if remove_pos < 0:
                remove_pos += len(self.board)
            self.score[self.scoring_player] += self.board.pop(remove_pos)

            # update position/marble/round
            self.current_pos = remove_pos if remove_pos < len(self.board) else 0
            self.current_marble += 1
            self.current_round += 1

            if DEBUG:
                print(self.score)

        if DEBUG:
            print(self)
        else:
            self.bar.next()

        return self.current_round

# ------------------------------------------------
# load config
# ------------------------------------------------
with open(INPUT) as f:
    nplayers, last_marble = map(int, re.sub('[^0-9;]', '', f.readline()).split(';'))

# ------------------------------------------------
# example
# ------------------------------------------------
if DEBUG:
    g = MarbleGame(9, 25)
    while g.next_round() is not None:
        pass
    print('')
    print(g.score)
    sys.exit(0)

# ------------------------------------------------
# part 1
# ------------------------------------------------
g = MarbleGame(nplayers, last_marble)
while g.next_round() is not None:
    pass
print('')
print(max(g.score))

# ------------------------------------------------
# part 2 - slow! (insertion in big lists is slow)
# ------------------------------------------------
g = MarbleGame(nplayers, 100 * last_marble)
while g.next_round() is not None:
    pass
print('')
print(max(g.score))

# vim:sts=4:sw=4:et:
