# -*- coding: utf-8 -*-

"""Drawing with alpha values."""

####

import pygame
import os

####

def load_pic(name, path="data"):

    pic = pygame.image.load(os.path.join(path, name))
    if pic.get_alpha():
        return pic.convert_alpha()
    else:
        return pic.convert()

####

def check(x, minval=0, maxval=255):

    return min(maxval, max(minval, x))

####

def offset(len1, len2):
    """ For picture centering"""
    return max(0, (len1 - len2) // 2)

####

class PeepDemo(object):


    def __init__(self, conf):

        pygame.init()
        self.width = conf['width']
        self.height = conf['height']
        self.fps = conf['fps']
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Move Mouse and Scroll Mouse Wheel")

        self.pic = load_pic(conf['pic'])
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(conf['backcol'])

        self.alpha_surface = pygame.Surface(self.screen.get_size(), flags=pygame.SRCALPHA)
        wo = offset(self.width, self.pic.get_width())
        ho = offset(self.height, self.pic.get_height())
        self.pic_offset = wo, ho

        # init stuff for circles with alpha value
        self.center = self.width // 2, self.height // 2
        self.max_radius = min(self.width, self.height)
        self.hole_count = conf['holes']
        self.calc_centers(self.center, self.center, self.hole_count)
        self.calc_rad_alphas(self.max_radius, self.hole_count)


    def calc_rad_alphas(self, radius, n):
        """Calculate linear radius and alpha values."""
        assert 0 < n < 256, "Invalid number of holes!"

        rad_step = radius // n
        alpha_step = 256 // n
        self.rad_alphas = [(radius - i * rad_step, 255 - i*alpha_step) for i in range(n)]


    def calc_centers(self, center, pos, holes):
        """Calculate center points from center (of window) to mouse position."""

        cx, cy = center
        mx, my = pos
        vx, vy = mx - cx, my - cy

        xs = vx // holes
        ys = vy // holes
        self.centers = [(cx + xs*i, cy + ys*i) for i in range(holes)]


    def run(self):
        """Mainloop"""
        mainloop = True
        while mainloop:
            self.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False
                elif event.type == pygame.MOUSEMOTION:
                    self.calc_centers(self.center, pygame.mouse.get_pos(),
                                      self.hole_count)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # check mouse wheel
                    if event.button in (4, 5):
                        self.hole_count = check(self.hole_count+ [-1, 1][event.button-4],
                                                2, 64)
                        self.calc_rad_alphas(self.max_radius, self.hole_count)
                        self.calc_centers(self.center, pygame.mouse.get_pos(),
                                          self.hole_count)

            self.show()
        pygame.quit()


    def show(self):
        """Draw all."""

        # picture on screen
        self.screen.blit(self.pic, self.pic_offset)
        # circles on alpha surface
        for (r, a), c in zip(self.rad_alphas, self.centers):
            pygame.draw.circle(self.alpha_surface, (0, 0, 0, a), c, r)

        # alpha surface on screen
        self.screen.blit(self.alpha_surface, (0, 0))
        # erase alpha surface for new circles
        self.alpha_surface.fill((0, 0, 0))


    def flip(self):
        """Show drawing and erase."""
        pygame.display.flip()
        self.screen.blit(self.background, (0, 0))
        self.clock.tick(self.fps)

####

CONFIG = {'width': 800,
          'height': 600,
          'backcol': (255, 0, 0),
          'fps': 100,
          'fontsize': 18,
          'pic': 'ente.jpg',
          'holes': 7}
####

if __name__ == "__main__":

    PeepDemo(CONFIG).run()
