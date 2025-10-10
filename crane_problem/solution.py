#!/usr/bin/env python3
import sys
from math import ceil
from enum import Enum
from functools import total_ordering
from itertools import product
from dataclasses import dataclass

@total_ordering
@dataclass
class Point:
    x: float
    y: float
    left: bool
    index: int = None

    def __eq__(self, o):
        return self.x == o.x and self.left == o.left

    def __lt__(self, o):
        if self.x == o.x:
            return self.left
        return self.x < o.x

@dataclass
class Line:
    slope: float
    yint: float
    vert: bool = False

    @classmethod
    def from_points(cls, p1, p2):
        if p1.x == p2.x:
            return cls(0, p1.x, True)
        slope = (p2.y - p1.y) / (p2.x - p1.x)
        yint = p1.y - p1.x * slope
        return cls(slope, yint)

    def __getitem__(self, x):
        if self.vert:
            raise Exception
        return self.slope * x + self.yint

@dataclass
class Segment:
    p1: Point
    p2: Point

    def __getitem__(self, k):
        return self.p2 if k else self.p1

    def intersects(self, line: Line):
        if line.vert:
            if self.p1.x == line.yint or self.p2.x == line.yint:
                return True
            return (self.p1.x < line.yint) ^ (self.p2.x < line.yint)
        y1 = line[self.p1.x]
        if y1 == self.p1.y:
            return True
        y2 = line[self.p2.x]
        if y2 == self.p2.y:
            return True
        return (y2 > self.p2.y) ^ (y1 > self.p1.y)

def parse_input(lines):
    l, n = next(lines).split()
    l = float(l)
    l_square = l ** 2
    n = int(n)
    segments = []
    for i in range(n):
        ax, ay, bx, by = [float(x) for x in next(lines).split()]
        if ax == bx and ay == by:
            # object already at destination
            continue
        midx = (ax + bx) / 2
        midy = (ay + by) / 2
        dist = (abs(ax - bx) ** 2 + abs(ay - by) ** 2) ** 0.5
        rad = dist / 2
        if rad > l:
            return None
        offset = (l_square - rad ** 2) ** 0.5
        perp_y = ax - bx
        perp_x = by - ay
        perp_x /= dist
        perp_y /= dist
        x1 = midx + perp_x * offset
        x2 = midx - perp_x * offset
        if x1 == x2:
            left = y1 < y2
        else:
            left = x1 < x2
        p1 = Point(x1, midy + perp_y * offset, left)
        p2 = Point(x2, midy - perp_y * offset, not left)
        segments.append(Segment(p1, p2))
    return segments

def parse_stdin():
    class stdin:
        def __next__(self):
            return input()
    return parse_input(stdin())

def parse_file(fn):
    with open(fn) as f:
        return parse_input(iter(f.readlines()))

def find_line_slow(segments):
    """This solution is O(n ** 3). This is not optimal."""
    for i, s1 in enumerate(segments):
        for j in range(i, len(segments)):
            s2 = segments[j]
            if i == j:
                pairs = [[0, 1]]
                pairs = [[0, 1]]
            else:
                pairs = product(range(2), range(2))
            for pair in pairs:
                p1 = s1[pair[0]]
                p2 = s2[pair[1]]
                l = Line.from_points(p1, p2)
                for s3 in segments:
                    if not s3.intersects(l):
                        break
                else:
                    return l
    return None

@total_ordering
class Event:
    def __init__(self, p1, p2, same_segment):
        self.p1 = p1
        self.p2 = p2
        self.same_segment = same_segment
        self.line = Line.from_points(p1, p2)

    def __eq__(self, o):
        s = self.line
        l = o.line
        if s.vert and l.vert:
            return True
        return s.slope == l.slope

    def __lt__(self, o):
        s = self.line
        l = o.line
        if s.vert:
            return not l.vert
        if l.vert:
            return False
        return s.slope < l.slope

    def __repr__(self):
        return f'{self.line} {self.p1} {self.p2} {self.same_segment}'

class State(Enum):
    left = 0
    middle = 1
    right = 2
    none = 3

    @staticmethod
    def combine(s1, s2):
        if s1 == State.none or s2 == State.none:
            return State.none
        if s1 == State.left:
            if s2 == State.left:
                return State.left
            return State.middle
        if s1 == State.middle:
            if s2 == State.right:
                return State.middle
            return State.none
        # s1 == State.right
        if s2 == State.right:
            return State.right
        return State.none

class SegmentTree:
    def __init__(self, arr, combine):
        levels = [arr]
        while len(levels[-1]) > 1:
            prev = levels[-1]
            layer_size = ceil(len(prev) / 2)
            level = []
            for i in range(layer_size):
                c1, c2 = i * 2, i * 2 + 1
                if c2 == len(prev):
                    level.append(prev[c1])
                else:
                    level.append(combine(prev[c1], prev[c2]))
            levels.append(level)
        self.levels = levels
        self.combine = combine

    def head(self):
        return self.levels[-1][0]

    def __setitem__(self, i, val):
        self.levels[0][i] = val
        for l in range(1, len(self.levels)):
            p = i // 2
            if i % 2:
                left, right = i - 1, i
            else:
                left, right = i, i + 1
            if right == len(self.levels[l - 1]):
                right -= 1
            self.levels[l][p] = self.combine(self.levels[l - 1][left], self.levels[l - 1][right])
            i = p

    def __str__(self):
        return '\n'.join(str(l) for l in reversed(self.levels))

def find_line_fast(segments):
    """This solution is O(n ** 2 * log(n)). It might be optimal but I don't know for certain."""
    events = []
    for i, s1 in enumerate(segments):
        for j in range(i, len(segments)):
            s2 = segments[j]
            if i == j:
                pairs = [[0, 1]]
            else:
                pairs = product(range(2), range(2))
            for pair in pairs:
                p1 = s1[pair[0]]
                p2 = s2[pair[1]]
                events.append(Event(p1, p2, i == j))
    events.sort()
    points = []
    for s in segments:
        points.append(s[0])
        points.append(s[1])
    points.sort()
    for i, p in enumerate(points):
        p.index = i
    arr = [State.left if p.left else State.right for p in points]
    st = SegmentTree(arr, State.combine)
    if st.head() == State.middle:
        return True
    for e in events:
        i, j = e.p1.index, e.p2.index
        e.p1.index, e.p2.index = j, i
        if e.same_segment:
            e.p1.left, e.p2.left = e.p2.left, e.p1.left
        st[i] = State.left if e.p2.left else State.right
        st[j] = State.left if e.p1.left else State.right
        if st.head() == State.middle:
            return True
    return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        segments = parse_file(sys.argv[1])
    else:
        segments = parse_stdin()
    #if segments is not None and (not len(segments) or find_line_slow(segments)):
    if segments is not None and (not len(segments) or find_line_fast(segments)):
        print('POSSIBLE')
    else:
        print('IMPOSSIBLE')

