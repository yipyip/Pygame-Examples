#!/usr/bin/env python3.3
# -*- coding: utf-8 -*-

"""Display framerate and playtime.
"""

####

import pygame

####

class PygView(object):


    def __init__(self, width=800, height=600, fps=50):
        """Initialize pygame, window, background, font,...
        """
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = width // 4
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', self.height // 7, bold=True)


    def run(self):
        """Mainloop.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            self.draw_text("FPS: %6.3f%sPLAYTIME: %6.3f SECONDS" %
                           (self.clock.get_fps(), " "*5, self.playtime))

            self.flip()

        pygame.quit()


    def flip(self):

        pygame.display.flip()
        self.clock.tick(self.fps)
        #self.screen.blit(self.background, (0, 0))
        self.screen.fill((0, 0, 0))


    def draw_text(self, text):
        """Center text in window.
        """
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, (0, 255, 0))
        self.screen.blit(surface, ((self.width - fw) // 2, (self.height - fh) // 2))

####

if __name__ == '__main__':

    PygView().run()
