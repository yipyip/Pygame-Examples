#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Version of 'Game of Life'."""

####

import pygame
import sys
import random

####

WIDTH = 800
HEIGHT = 600
CELL_WIDTH = 8
CELL_HEIGHT = 6

MAX_X = WIDTH // CELL_WIDTH
MAX_Y = HEIGHT // CELL_HEIGHT

OFFSETS = ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))
CELL_COLOR = (0, 255, 0)

####

def init_pygame(width, height):

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Conway's Game of Life (ESC to quit)")

    return screen, clock

####

def populate_cells(max_x, max_y, ratio=8):

    cells = {}
    for y in range(max_y):
        for x in range(max_x):
            cells[x, y] = random.choice(([0] * ratio) + [1])

    return cells

####

def dead_or_alive(old_cells, x, y, new_cells):
    """Check Rules:
           dead cell   => living cell, if exactly 3 neighbors
           living cell => dead cell, if not 2 or 3 neighbors
    """
    neighbors = sum(old_cells[(MAX_X+x+i)%MAX_X, (MAX_Y+y+j)%MAX_Y] for i, j in OFFSETS)

    if old_cells[x, y] == 0:
        if neighbors == 3:
            new_cells[x, y] = 1
        else:
            new_cells[x, y] = 0
    else:
        if neighbors in (2, 3):
            new_cells[x, y] = 1
        else:
            new_cells[x, y] = 0

####

def simulate(screen, clock):
    """The main part.

    Check cells in old map and write results in new map.
    """
    old_cells = populate_cells(MAX_X, MAX_Y)
    new_cells = {}

    running = True
    while running:

        screen.fill((20, 20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

        for y in range(MAX_Y):
            for x in range(MAX_X):
                if old_cells[x, y]:
                    pygame.draw.rect(screen, CELL_COLOR,
                                     (x * CELL_WIDTH, y*CELL_HEIGHT,
                                      CELL_WIDTH, CELL_HEIGHT))
                dead_or_alive(old_cells, x, y, new_cells)

        old_cells = new_cells
        new_cells = {}
        clock.tick(200)
        pygame.display.update()

    pygame.quit()

####

if __name__ == '__main__':

    screen, clock = init_pygame(WIDTH, HEIGHT)
    simulate(screen, clock)
