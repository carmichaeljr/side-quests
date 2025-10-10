import sys
import numpy as np
from generation import DatasetGen
import matplotlib.pyplot as plt
from matplotlib import collections as mc
import pylab as pl

g = DatasetGen()

def parse_file(fn):
    with open(fn) as f:
        lines = iter(f.readlines())
    l, n = next(lines).split()
    l = float(l)
    l_square = l ** 2
    n = int(n)
    segments = []
    for i in range(n):
        ax, ay, bx, by = [float(x) for x in next(lines).split()]
        p1 = ax, ay
        p2 = bx, by
        #p1, p2 = g.convert_segment(p1, p2, l)
        segments.append((p1, p2))
    return l, segments

def main(fn):
    l, segments = parse_file(fn)
    red = np.linspace(0, 1, len(segments))
    green = [0] * len(segments)
    blue = 1 - red
    alpha = [1] * len(segments)
    colors = list(zip(red, green, blue, alpha))
    converted = []
    for p1, p2 in segments:
        p1, p2 = g.convert_segment(p1, p2, l)
        if p1 is None:
            print('IMPOSSIBLE, a segment is empty')
            continue
        converted.append((p1, p2))
    lc = mc.LineCollection(converted, colors=colors, linewidths=2)
    fig, ax = pl.subplots()
    ax.add_collection(lc)
    border = 60
    ax.set_ylim(-border, 100 + border)
    ax.set_xlim(-border, 100 + border)
    ax.margins(0.1)
    plt.show()

if __name__ == '__main__':
    fn = sys.argv[1]
    main(fn)
