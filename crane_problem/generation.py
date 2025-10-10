import subprocess
import numpy as np
import shutil
from pathlib import Path
from io import StringIO
import time
import random

SOLUTION_CMD = 'python3 solution.py'

class DatasetGen:
    def __init__(self):
        self.number = 0
        self.output_dir = Path('testcases/output')
        self.input_dir = Path('testcases/input')

    def solve(self, l, segments):
        s = StringIO()
        self.write(l, segments, s)
        cp = subprocess.run(SOLUTION_CMD, input=s.getvalue().encode(), stdout=subprocess.PIPE, shell=True)
        result = cp.stdout.decode().strip()
        return result == 'POSSIBLE'

    def write(self, l, segments, f):
        f.write(f'{l:.2f} {len(segments)}\n')
        for p1, p2 in segments:
            ax, ay = p1
            bx, by = p2
            f.write(f'{ax:.2f} {ay:.2f} {bx:.2f} {by:.2f}\n')

    def output(self, l, segments, answer=None):
        in_fn = self.input_dir / f'input{self.number:02d}.txt'
        out_fn = self.output_dir / f'output{self.number:02d}.txt'
        with open(in_fn, 'w') as f:
            self.write(l, segments, f)
        t1 = time.time()
        if answer is None:
            with open(in_fn) as in_f, open(out_fn, 'w') as out_f:
                subprocess.run(SOLUTION_CMD, stdin=in_f, stdout=out_f, shell=True)
        else:
            with open(out_fn, 'w') as f:
                f.write(f'{answer}\n')
        print(f'Case {self.number} took {time.time() - t1:.2f} sec')
        self.number += 1

    def cleanup(self):
        shutil.rmtree('testcases', ignore_errors=True)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.input_dir.mkdir(exist_ok=True, parents=True)
        out = Path('testcases.zip')
        if out.exists():
            out.unlink()

    def generate(self):
        self.cleanup()
        funcs = [a for a in dir(self) if a.startswith('gen_') and callable(getattr(self, a))]
        funcs.sort(key=lambda x: x == 'gen_sample', reverse=True)
        for func in funcs:
            print(func)
            getattr(self, func)()
        subprocess.run('zip testcases.zip -qrxi testcases', shell=True)
    
    def convert_segment(self, p1, p2, l):
        l_square = l ** 2
        ax, ay = p1
        bx, by = p2
        midx = (ax + bx) / 2
        midy = (ay + by) / 2
        dist = (abs(ax - bx) ** 2 + abs(ay - by) ** 2) ** 0.5
        rad = dist / 2
        if rad > l:
            return None, None
        offset = (l_square - rad ** 2) ** 0.5
        perp_y = ax - bx
        perp_x = by - ay
        perp_x /= dist
        perp_y /= dist
        x1 = midx + perp_x * offset
        x2 = midx - perp_x * offset
        n1 = x1, midy + perp_y * offset
        n2 = x2, midy - perp_y * offset
        return n1, n2

    def uniform_segments(self, bounds, count):
        segments = []
        for _ in range(count):
            p1 = random.random() * bounds, random.random() * bounds
            p2 = random.random() * bounds, random.random() * bounds
            segments.append((p1, p2))
        return segments

    def gen_random(self):
        random.seed(59823)
        segments = self.uniform_segments(100, 10)
        self.output(50, segments)
        self.output(70, segments)
        for _ in range(20):
            segments = self.uniform_segments(100, 10)
            if self.solve(50, segments):
                self.output(60, segments)
            else:
                self.output(40, segments)

    def gen_grid(self):
        '''TODO redo so that we actually have n**2 intersections. Insert an
        impossible segment at different locations in the list.'''
        return
        n = 200
        l = 1.1
        segments = []
        for i in range(n):
            i *= 2
            p1 = i + 1, 1
            p2 = i + 1, -1
            segments.append((p1, p2))
            p1 = 1, i + 1
            p2 = -1, i + 1
            segments.append((p1, p2))
        self.output(l, segments)

    def gen_cubed(self):
        """Takes just under 10 seconds w/ my n^2logn solution. Takes over 30
        sec with n^3 solution."""
        l = 1.5
        count = 560
        impossible = (
            ((-1, 10), (1, 10)),
            ((10, -1), (10, 1))
        )
        for location in range(0, count + 1, 20):
            segments = []
            for i, theta in enumerate(np.linspace(0, np.pi / 2, count)):
                p1 = np.sin(theta), np.cos(theta)
                p2 = -p1[0], -p1[1]
                segments.append((p1, p2))
                if i == location:
                    segments.extend(impossible)
            if location == count:
                segments.extend(impossible)
            self.output(l, segments, answer='IMPOSSIBLE')
            #self.output(l, segments)

    def gen_simple_edgecases(self):
        l = 1
        segments = (((0, 0), (0, 1)),)
        self.output(l, segments)
        segments = (((0, 0), (1, 0)),)
        self.output(l, segments)
        # this one feels kinda evil but it's not wrong...
        segments = (((0, 0), (0, 0)),)
        self.output(l, segments)
        segments = (((0, 0), (0, 0)), ((0, 0), (0, 1)))
        self.output(l, segments)
        # overlapping vertical segments
        l = 10
        segments = []
        for i in range(1, 6):
            segments.append(((-i, 0), (i, 0)))
        self.output(l, segments)
        # overlapping horizontal segments
        l = 10
        segments = []
        for i in range(1, 6):
            segments.append(((0, -i), (0, i)))
        self.output(l, segments)

    def gen_collinear_edgecases(self):
        return
        # horizontal
        l = 5
        segments = []
        for i in range(0, 15, 7):
            segments.append(self.convert_segment((i, 0), (i + 6, 0), l))
        self.output(l, segments)
        # vertical
        segments = []
        for i in range(0, 15, 7):
            segments.append(self.convert_segment((0, i), (0, i + 6), l))
        self.output(l, segments)
        # y = x
        segments = []
        for i in range(0, 15, 7):
            segments.append(self.convert_segment((i, i), (i + 1, i + 1), l))
        self.output(l, segments)
        # exactly one solution that touches endpoints - vertical
        segments = []
        segments = (
            self.convert_segment((-1, 0), (-1, -6), l),
            self.convert_segment((1, 0), (1, -6), l),
            self.convert_segment((0, 0), (0, 6), l)
        )
        self.output(l, segments)
        # exactly one solution that touches endpoints - horizontal
        segments = []
        segments = (
            self.convert_segment((0, -1), (-6, -1), l),
            self.convert_segment((0, 1), (-6, 1), l),
            self.convert_segment((0, 0), (6, 0), l)
        )
        self.output(l, segments)
        # three horizontal lines

    def gen_sample(self):
        #l = 1
        #segments = (
        #    ((1, 1), (2, 2)),
        #    ((3, 2), (4, 1)),
        #    ((2, -1), (3, 0)),
        #)
        #self.output(l, segments)
        #return
        l = 1
        segments = (
            ((1, 2), (2, 1)),
            ((2, 0), (3, -1)),
            ((3, 1), (4, 2)),
        )
        self.output(l, segments)
        l = 1.41
        segments = (
            ((0, 2), (2, 2)),
            ((2, 2), (3, 1)),
            ((1.5, -2), (1.5, -2)),
        )
        self.output(l, segments)
        return
        l = 1.5
        segments = (((0, 0), (0, 1)),)
        self.output(l, segments)


if __name__ == '__main__':
    g = DatasetGen()
    g.generate()
    #g.cleanup()
    #g.gen_sample()
    #g.gen_cubed()
    #g.gen_grid()
    #g.gen_collinear_edgecases()
    # TODO edge cases
    # - exactly one possible solution
    #   - solution is vertical
    #   - solution is horizontal
    # - negative/positive numbers
    # - cross through origin
    #   - vertical/horizontal
    # - overlapping lines?
    # TODO idea for n**3 slowness
    # - small segment high up
    # - small segment over to the right
    # - a ton of intersecting segments in the middle
    # - IMPOSSIBLE
    # TODO rewrite solution in C++
    # - force n**2 logn solution
    # - there is no way n**2 logn python will beat n**2 C++ in reasonable time
