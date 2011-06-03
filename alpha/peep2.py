#!/usr/bin/env python

"""
per-pixel-alpha demo
"""
  
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
    """ For picture centering
    """
    return max(0, (len1 - len2) // 2)

####

class PeepDemo(object):


    def __init__(self, **opts):

        pygame.init()
        self.width = opts['width']
        self.height = opts['height']
        self.fps = opts['fps']
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Move Mouse and Scroll Mouse Wheel")

        self.pic = load_pic(opts['pic'])
        self.background = pygame.Surface(self.screen.get_size()).convert()  
        self.background.fill(opts['backcol'])

        self.ppa_surface = pygame.Surface(self.screen.get_size(), flags=pygame.SRCALPHA)
        self.pic_offset = offset(self.width, self.pic.get_width()),\
                          offset(self.height, self.pic.get_height())

        self.center = self.width // 2, self.height // 2
        self.max_radius = min(self.width, self.height)
        self.hole_count = opts['holes']
        self.calc_centers(self.center, self.center, self.hole_count)
        self.calc_rad_alphas(self.max_radius, self.hole_count)


    def calc_rad_alphas(self, radius, n):
        
        assert 0 < n < 256, "Invalid number of holes!"

        rad_step = radius // n
        alpha_step = 256 // n
        self.rad_alphas = [(radius - i * rad_step, 255 - i*alpha_step) for i in xrange(n)]
             

    def calc_centers(self, center, pos, holes):

        cx, cy = center
        mx, my = pos 
        vx, vy = mx - cx, my - cy

        xs = vx // holes
        ys = vy // holes
        self.centers = [(cx + xs*i, cy + ys*i) for i in xrange(holes)]

        
    def run(self):
        """
        Mainloop
        """
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
                    self.calc_centers(self.center, pygame.mouse.get_pos(), self.hole_count)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in (4, 5):
                        self.hole_count = check(self.hole_count+ [-1, 1][event.button-4], 2, 64)  
                        self.calc_rad_alphas(self.max_radius, self.hole_count)
                        self.calc_centers(self.center, pygame.mouse.get_pos(), self.hole_count)
                        
            self.show()
        pygame.quit()
            
   
    def show(self):

        self.screen.blit(self.pic, self.pic_offset)
        for (r, a), c in zip(self.rad_alphas, self.centers):
            #print c
            pygame.draw.circle(self.ppa_surface, (0, 0, 0, a), c, r)

        self.screen.blit(self.ppa_surface, (0, 0))
        self.ppa_surface.fill((0, 0, 0))
        
 
    def flip(self):

         pygame.display.flip()
         self.screen.blit(self.background, (0, 0))
         self.clock.tick(self.fps)
            
####

opts = {'width': 800,
        'height': 600,
        'backcol': (255, 0, 0),
        'fps': 10,
        'fontsize': 18,
        'pic': 'ente.jpg',
        'holes': 7}
####

if __name__ == "__main__":

    PeepDemo(**opts).run()
