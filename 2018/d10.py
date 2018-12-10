#!/usr/bin/env python3
import sys
import re
from matplotlib import pyplot
import numpy
from pprint import pprint

INPUT = 'd10-input.txt'
line_re = re.compile('position=< *(?P<x>-?\d+), *(?P<y>-?\d+)> *velocity=< *(?P<vx>-?\d+), *(?P<vy>-?\d+)>.*')

# ------------------------------------------------
# helper functions
# ------------------------------------------------
def update(points, speeds, reverse=False):
    if not reverse:
        for i, v in enumerate(speeds):
            p = points[i]
            points[i] = (p[0]+v[0], p[1]+v[1])
    else:
        for i, v in enumerate(speeds):
            p = points[i]
            points[i] = (p[0]-v[0], p[1]-v[1])

def area(points):
    min_ = list(map(min,zip(*points)))
    max_ = list(map(max,zip(*points)))
    return(tuple(zip(min_, max_)))

def make_plot(points, plot_area=None):
    if plot_area is None:
        a = area(points)
    else:
        a = plot_area
    gridw = a[0][1] - a[0][0] + 1
    gridh = a[1][1] - a[1][0] + 1

    plot_data = numpy.zeros((gridh, gridw))
    plot_points = [(p[1]-a[1][0], p[0]-a[0][0]) for p in points]
    plot_data[tuple(zip(*plot_points))] = 1

    img = pyplot.imshow(plot_data, cmap='brg') 
    pyplot.show()
    return (a, img)

# ------------------------------------------------
# scan input
# ------------------------------------------------
points = []
speeds = []
with open(INPUT) as f:
    for ln, line in enumerate(f):
        m = line_re.match(line)
        if m is None:
            print('Bad input on line %d: %s' % (ln, line.strip()), file=sys.stderr)
            sys.exit(1)
        points.append( (int(m['x']), int(m['y'])) )
        speeds.append( (int(m['vx']), int(m['vy'])) )

# ------------------------------------------------
# part 1 and 2
# ------------------------------------------------
# Points start dispersed on the grid. We quantify the dispersion by
# measuring the number of unique x and y coordinates.
#
# We can't be sure when the points will form the secret message. But
# when they do, the number of unique x and y coordinates will be less
# than when we started. They will remain so for a while and then the
# points will start to disperse again.
#
# We print all frames after the number of unique points have started
# reducing and before the points start dispersing again.

# number of unique x/y coordinates
len_ux_init = len(set([p[0] for p in points]))
len_uy_init = len(set([p[1] for p in points]))

# do we consider the points dispersed?
dispersed = True

# initial area when we start plotting
plot_area = None

# current step
step = 0

while True:
    step += 1
    update(points, speeds)
    ux = set([p[0] for p in points])
    uy = set([p[1] for p in points])
    if len(ux) < len_ux_init and len(uy) < len_uy_init:
        # points are no longer dispersed
        dispersed = False
        try:
            print('Plotting frame %d (len_ux=%d, len_uy=%d).' % (step, len(ux), len(uy)), end=' ')
            print("Press 'q' in plot window for next frame...")
            plot_area, img = make_plot(points, plot_area)
        except IndexError:
            # points are dispersed again
            dispersed = True
            break
    elif not dispersed and len(ux) >= len_ux_init and len(uy) >= len_uy_init:
        # points are dispersed again
        dispersed = True
        break

# vim:sts=4:sw=4:et:
