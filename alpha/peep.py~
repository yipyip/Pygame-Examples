#!/usr/bin/env python

"""
Usage of colorkey
"""
  
####

import pygame
import os

####

def load_pic(name, path="data"):

    pic = pygame.image.load(os.path.join(path, name))
    if pic.get_alpha():
        #print "%s has alpha" % name
        return pic.convert_alpha()
    else:
        #print "%s has no alpha" % name
        return pic.convert()

####

class ColorkeyDemo(object):


    def __init__(self, **opts):

        pygame.init()
        width, height = opts['width'], opts['height']
        self.fps = opts['fps']
        self.screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
        self.font = pygame.font.SysFont('mono', opts['fontsize'], bold=True)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Colorkey Demo")

        self.background = pygame.Surface(self.screen.get_size()).convert()  
        self.background.fill(opts['backcol'])
        
        self.pic = load_pic(opts['pic'])
        basename, self.extension = os.path.splitext(opts['pic'])
        self.backpic = pygame.transform.scale(self.pic, (width, height))
        self.forepic = self.pic.copy()


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
           
            self.action(pygame.key.get_pressed())
           

    def action(self, pressed_keys):

        self.show_surfaces(self.forepic, self.extension, 0, 0,
                           self.forepic.get_width(), self.forepic.get_height())

   
    def show_surfaces(self, surf, pictype, x, y, x_delta, height):
        
        yh = y + height       
        #pure surface
        self.screen.blit(surf, (x, y))
        self.write(x, yh, "%s pure" % pictype)
        
        # with with colorkey
        x += x_delta 
        ck_surf = surf.copy()
        ck_surf.set_colorkey(ck_surf.get_at((0, 0)))
        self.screen.blit(ck_surf, (x, y))
        self.write(x, yh, "%s colorkey" % pictype)
        
 
    def flip(self):

         pygame.display.flip()
         self.clock.tick(self.fps)
         self.screen.blit(self.background, (0, 0))
         

    def write(self, x, y, msg, color=(255,255,0)):

        self.screen.blit(self.font.render(msg, True, color), (x, y))

            
####

opts = {'width': 600,
        'height': 400,
        'backcol': (144, 144, 144),
        'fps': 10,
        'fontsize': 18,
        'pic': 'colormonster.jpg'}
####

if __name__ == "__main__":

    ColorkeyDemo(**opts).run()
