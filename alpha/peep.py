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
        pygame.display.set_caption("per-pixel-alpha Demo")

        self.pic = load_pic(opts['pic'])
        self.background = pygame.Surface(self.screen.get_size()).convert()  
        self.background.fill(opts['backcol'])

        self.ppa_surface = pygame.Surface(self.screen.get_size(), flags=pygame.SRCALPHA)
        self.pic_offset = offset(self.width, self.pic.get_width()),\
                          offset(self.height, self.pic.get_height())                    
        self.make_holes(opts['holes'])


    def make_holes(self, n):

        assert 0 < n < 256, "Invalid number of holes!"
        
        radius = min(self.width, self.height)
        rad_step = radius // n
        alpha_step = 255 // n
        self.rad_alphas = [(radius - i * rad_step, 255 - i * alpha_step) for i in xrange(n)]
        self.center = self.width // 2, self.height // 2
            

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
            self.show()

        pygame.quit()
            
   
    def show(self):

        self.screen.blit(self.pic, self.pic_offset)
        for r, a in self.rad_alphas:
            pygame.draw.circle(self.ppa_surface, (0, 0, 0, a), self.center, r)

        self.screen.blit(self.ppa_surface, (0, 0))
        
 
    def flip(self):

         pygame.display.flip()
         self.clock.tick(self.fps)
         self.screen.blit(self.background, (0, 0))
         

    def write(self, x, y, msg, color=(255,255,0)):

        self.screen.blit(self.font.render(msg, True, color), (x, y))

            
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
