#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Blinking rectangles."""

####

import pygame as pyg
import itertools as it

####

class Grid(object):
    """A Grid Abstraction"""
    
    def __init__(self, dx=1, dy=1, width=1, height=1, xoff=0, yoff=0):
        """dx, dy should be > 0"""
        self.dx = dx
        self.dy = dy
        self.width= width
        self.height= height
        self.xoff = xoff
        self.yoff = yoff


    def __call__(self, x, y):
        """Convert grid coordinates to canvas coordinates."""
        return self.xoff + x * self.dx, self.yoff + y * self.dy


    def box(self, x, y):
        """Return rectangle parameters for pygame."""
        return self(x, y) + (self.width, self.height)

####

class Display(object):
    """Pygame Stuff"""

    def __init__(self, controller, grid, width, height, backcol=(0, 0, 0), fps=30):

        self.controller = controller
        self.grid = grid
        self.width = width
        self.height = height
        self.backcol = backcol
        self.fps = fps
        self.quit_keys = pyg.K_ESCAPE, pyg.K_q

        pyg.init()
        self.canvas = pyg.display.set_mode((width, height), pyg.FULLSCREEN|pyg.DOUBLEBUF)


    def run(self):

        running = True
        clock = pyg.time.Clock()
        while running:
            clock.tick(self.fps)
            running = self.dispatch_events()
            self.controller.process()
            self.flip()
        else:
            self.quit()


    def dispatch_events(self):

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                return False
            if event.type == pyg.KEYDOWN:
                if event.key in self.quit_keys:
                    return False
        else:
            return True


    def set_color(self, rgb):

        self.act_color = rgb


    def rect(self, x, y):

        pyg.draw.rect(self.canvas, self.act_color, self.grid.box(x, y))


    def flip(self):

        pyg.display.flip()
        self.canvas.fill(self.backcol)


    def quit(self):

        pyg.quit()


####

class LedColumn(object):
    """A Column of Rectangles (the LEDs)."""

    def __init__(self, colors):

        self.colors = colors
        self.states = [0] * len(colors)


    def __getitem__(self, i):

        return self.colors[i], self.states[i]


    def __setitem__(self, i, on_off):

        self.states[i] = on_off

####

class LedMatrix(object):
    """Coluns and Rows"""

    def __init__(self, columns, rows, colors):

        self.rows = rows
        self.columns = columns
        self.mat = [LedColumn(colors[row]) for row in xrange(columns)]
        self.act_column = it.cycle(range(columns))


    def __getitem__(self, column):

        return self.mat[column]


    def set_led(self, column, row, on_off):

        self[column].states[row] = on_off


    def draw_column(self, device):

        column = self.act_column.next()
        for i, (col, state) in enumerate(self[column]):
            if state:
                device.set_color(col)
                device.rect(column, i)

####

class Controller(object):
    """The C in MVC"""

    def __init__(self, demo, grid, width, height, fps):

        self.demo = demo
        self.display = Display(self, grid, width, height, fps)


    def process(self):

        self.demo.animate(self.display)


    def run(self):

        self.display.run()

####

class Demo(object):
    """The Model in MVC"""

    def __init__(self, columns, rows, speed=100, one_column=False):

        colors = [[((0, 255, 0), (255, 0, 0))[(c+r) % 2] for r in xrange(rows)]
                  for c in xrange(columns)]
        self.matrix = LedMatrix(columns, rows, colors)
        self.xs = it.cycle(xrange(columns))
        self.ys = it.cycle(xrange(rows))
        self.duration = it.cycle(xrange(max(1, speed)))
        self.ax = 0
        self.ay = 0
        self.columns = columns
        self.one_column = one_column


    def animate(self, display):

        if not self.duration.next():
            self.ax = self.xs.next()
        if not self.ax:
            self.ay = self.ys.next()

        self.matrix.set_led(self.ax, self.ay, 0)

        if self.one_column:
            self.matrix.draw_column(display)
        else:
            for _ in self.matrix:
                self.matrix.draw_column(display)

        self.matrix.set_led(self.ax, self.ay, 1)

####

def main():

    width = 800
    height = 600

    ## experimentation values
    columns = 12
    rows = 8
    xspace = 10
    yspace = 10
    fps = 30
    speedfac = 0.03
    # 1 column per frame flag
    one_column = False #True

    dx = width // columns
    dy = height // rows
    grid = Grid(dx, dy, dx - xspace, dy - yspace, xspace // 2, yspace // 2)
    demo = Demo(columns, rows, int(fps * speedfac), one_column)
    Controller(demo, grid, width, height, fps).run()

####

if __name__ == '__main__':

    main()

