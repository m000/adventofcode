#!/usr/bin/env python3
import sys
import re
from pprint import pprint
from termcolor import colored
from progress.bar import IncrementalBar

INPUT = 'd09-input.txt'
DEBUG = False
DEBUG_SCORE = False

# ------------------------------------------------
# Class modeling the game.
# ------------------------------------------------
class MarbleBoard:
    ''' Caching marble board.

        The cache contains the board state near the current position.
        Because the cache is small it is faster to insert marbles in the
        cache and sync it with the global board state once in a while.
        The default cache_block seems to work reasonably well.

        In general, a linked-list based implementation would probably work
        even better, since we don't have random accesses to the game state.
    '''
    def __init__(self, initial=None, cache_block=2**12):
        self.cache_block = cache_block
        self.board = initial.copy()
        self.cache = None
        self.cache_flush(0)

    @property
    def cend(self):
        return self.cstart + len(self.cache)

    @property
    def cgrowth(self):
        return len(self.cache) - self.csize_init

    def __len__(self):
        return len(self.board) + self.cgrowth

    def __str__(self):
        return '%s(cache_block=%d)\n\t%s\n\t%s\n\t%s' % (
                self.__class__.__name__,
                self.cache_block,
                self.board, self.cache, self.cache_dirty)

    def __iter__(self):
        return self

    def __next__(self):
        if not hasattr(self, '_i'):
            self._i = 0
        while self._i < len(self):
            v = self[self._i]
            self._i += 1
            return v
        del self._i
        raise StopIteration

    def __getitem__(self, pos):
        if pos < self.cstart:
            return self.board[pos]
        elif pos > self.cend:
            return self.board[pos - self.cgrowth]
        else:
            return self.cache[pos - self.cstart]

    def pop(self, pos=None):
        pos = pos if pos is not None else len(self)
        if pos < self.cstart:
            self.cstart -= 1
            return self.board.pop(pos)
        elif pos > self.cend:
            return self.board.pop(pos - self.cgrowth)
        else:
            self.cache_dirty.pop(pos - self.cstart)
            return self.cache.pop(pos - self.cstart)

    def insert(self, pos, item):
        if (len(self.cache) > 2*self.cache_block):
            self.cache_flush(pos)
        elif (pos < self.cstart or pos > self.cend + 1):
            self.cache_flush(pos)

        cache_pos = pos - self.cstart
        self.cache.insert(cache_pos, item)
        self.cache_dirty.insert(cache_pos, True)

    def cache_flush(self, pos):
        # flush
        if self.cache:
            self.board = self.board[:self.cstart] +\
                    self.cache +\
                    self.board[self.cstart + self.csize_init:]

        # reload
        self.cstart = pos
        self.cache = self.board[self.cstart : self.cstart+self.cache_block]
        self.cache_dirty = [False,] * len(self.cache)
        self.csize_init = len(self.cache)

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
        if DEBUG:
            print(self)
        else:
            self.bar = IncrementalBar(max=self.last_marble)

    def __str__(self):
        s_round = MarbleGame.round_fmt(self.current_marble - 1)
        s_marbles = ''.join([
            MarbleGame.mbold_fmt(m) if i == self.current_pos else MarbleGame.mplain_fmt(m)
            for i, m in enumerate(self.board)
            ])
        return '%s%s' % (s_round, s_marbles)

    @property
    def scoring_player(self):
        if self.current_marble > 0:
            return (self.current_marble - 1) % len(self.score)
        else:
            return None

    def finished(self):
        return self.current_marble > self.last_marble

    def next_round(self):
        if self.finished():
            if not DEBUG:
                self.bar.goto(self.current_marble)
            return None

        if self.current_marble % MarbleGame.score_multipleof != 0:
            self.current_pos = self.current_pos + 2
            if (self.current_pos > len(self.board)):
                self.current_pos -= len(self.board)
            self.board.insert(self.current_pos, self.current_marble)
            self.current_marble += 1
        else:
            if not DEBUG:
                self.bar.goto(self.current_marble)

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

            if DEBUG_SCORE:
                print(self.score)

        if DEBUG:
            print(self)

        return self.current_marble

class FastMarbleGame(MarbleGame):
    def __init__(self, *args, **kwargs):
        mbkwargs = {}
        if 'cache_block' in kwargs:
            mbkwargs['cache_block'] = kwargs.pop('cache_block')
        super().__init__(*args, **kwargs)
        self.board = MarbleBoard(initial=self.board, **mbkwargs)

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
    print('\n', g.score)

    g = FastMarbleGame(9, 25, cache_block=128)
    while g.next_round() is not None:
        pass
    print('\n', g.score)
    sys.exit(0)

# ------------------------------------------------
# part 1
# ------------------------------------------------
g = MarbleGame(nplayers, last_marble)
while g.next_round() is not None:
    pass
print('\n', max(g.score))

# ------------------------------------------------
# part 2 - slow! (insertion in big lists is slow)
# ------------------------------------------------
g = FastMarbleGame(nplayers, 100 * last_marble)
while g.next_round() is not None:
    pass
print('\n', max(g.score))

# vim:sts=4:sw=4:et:
