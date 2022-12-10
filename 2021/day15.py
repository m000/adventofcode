#!/usr/bin/env python3.10

import logging
from collections import namedtuple

import numpy as np

import aoc

Neighbours = namedtuple('Neighbours', ('n', 'e', 's', 'w'))

def write_array(m, filename, delim=' '):
    vmax = np.max(m)
    fieldw = len(str(vmax))
    print(f'{vmax:0{2*fieldw}}x')
    with open(filename, 'w') as f:
        for row in m:
            print(delim.join([f'{c:0{fieldw}d}' for c in row]), file=f)


def neighbours(i, j, data=None):
    all_neighbours = [
        (i - 1, j), (i, j + 1), (i + 1, j), (i, j - 1),
        #   n            e          s            w
    ]
    return Neighbours(*map(
        lambda n: n if n[0] >= 0 and n[1] >= 0 and n[0] < data.shape[0] and n[1] < data.shape[1] else None,
        all_neighbours
    ))


def expand_map(pweights, factor):
    pweights2 = np.zeros((factor * pweights.shape[0], factor * pweights.shape[1]), dtype=int)
    for i in range(0, factor):
        for j in range(0, factor):
            w = (slice(i * pweights.shape[0], (i + 1)*pweights.shape[0]),
                    slice(j * pweights.shape[1], (j + 1)*pweights.shape[1]))
            pweights2[w] = pweights + (i + j)
    pweights2[pweights2 > 9] += 1   # wrap-around to 1
    pweights2 %= 10
    return pweights2


def dijkstra(pweights, end):
    # NB: https://en.wikipedia.org/wiki/Dijkstra's_algorithm
    dist = np.full(pweights.shape, -1, dtype=int)
    visited = np.zeros(pweights.shape, dtype=bool)
    dist[0, 0] = 0  # starting position always 0, 0 - risk is not counted
    done = False
    while True:
        for (i, j) in zip(*np.where(visited == 0)):
            for n in filter(lambda n: n is not None and not visited[n], neighbours(i, j, pweights)):
                dist_through_ij = dist[i, j] + pweights[n]
                if dist[n] < 0 or dist_through_ij < dist[n]:
                    dist[n] = dist_through_ij
            visited[i, j] = True
            if (i, j) == end:
                done = True
                break
        if done:
            logging.info("DONE")
            break
        elif dist[end] < 0:
            logging.error("UNREACHABLE")
            raise RuntimeError("The end point is not reachable.")
        else:
            logging.error("NOT HANDLED")
            raise RuntimeError("Partially implemented algorithm.")
    return dist


if __name__ == '__main__':
    aoc.logging_setup()
    pweights = np.genfromtxt(
        aoc.input_file(15),
        dtype=int, delimiter=1,  # delimiter = 1 -> fields of width 1
    )

    # first part
    #dist = dijkstra(pweights, (pweights.shape[0]-1, pweights.shape[1]-1))
    #print(dist[-1, -1])

    # second part
    pweights2 = expand_map(pweights, 5)
    write_array(pweights2, 'foo.txt', delim='')

    #dist = dijkstra(pweights2, (pweights2.shape[0]-1, pweights2.shape[1]-1))
    #print(dist[-1, -1])

