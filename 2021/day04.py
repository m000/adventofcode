#!/usr/bin/env python3.10

import numpy as np

import aoc


def parse_input(specifier=None):
    bingo_numbers = None
    bingo_boards = []
    board_lines = []
    for ln in aoc.input(4, specifier):
        if ln == '':
            if board_lines:
                bingo_boards.append(np.genfromtxt(board_lines, dtype=int))
                board_lines = []
            continue
        if bingo_numbers is None:
            bingo_numbers = np.fromstring(ln, dtype=int, sep=',')
        else:
            board_lines.append(ln)
    bingo_boards.append(np.genfromtxt(board_lines, dtype=int))
    return (bingo_numbers, bingo_boards)


if __name__ == '__main__':
    bingo_numbers, bingo_boards = parse_input()
    bingo_found = [np.zeros(shape=b.shape, dtype=int) for b in bingo_boards]
    winners = {}
    for idxn, n in enumerate(bingo_numbers):
        for idxb, (b, bf) in filter(lambda t: t[0] not in winners, enumerate(zip(bingo_boards, bingo_found))):
            bf[b == n] = 1
            nrows, ncols = bf.shape
            if any([ncols in [np.count_nonzero(bf[i, :]) for i in range(nrows)],
                    nrows in [np.count_nonzero(bf[:, j]) for j in range(ncols)]]):
                winners[idxb] = (b, bf), (idxn, n)
        if len(winners) == len(bingo_boards):
            break
    else:
        raise ValueError(f"Only {len(winners)}/{len(bingo_boards)} were able to "
                         f"score a bingo with numbers {bingo_numbers}.")

    # first part
    idxb, ((b, bf), (idxn, n)) = min(winners.items(), key=lambda kv: kv[1][1][0])
    print(np.sum(b[bf == 0]) * n)

    # second part
    idxb, ((b, bf), (idxn, n)) = max(winners.items(), key=lambda kv: kv[1][1][0])
    print(np.sum(b[bf == 0]) * n)
