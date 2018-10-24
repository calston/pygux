import pygame
import time
import math

from pygame.locals import *

from pygux.widgets.widget import Widget, hlBox
from pygux.colours import Colours


class Sprite(Widget):
    def __init__(self, x, y, w, h, image=None, callback=None, **kw):
        """Sprite widget
        """
        Widget.__init__(self, x, y, w, h, **kw)

        if image:
            self.image = pygame.image.load(image).convert()
        else:
            self.image = None

        self.callback = callback


    def draw(self):
        surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        if self.image:
            my_img = pygame.transform.smoothscale(self.image, (self.w, self.h))
            surface.blit(my_img, (0, 0))
       
        self.parent.surface.blit(surface, (self.x, self.y))

    def touched(self, position):
        if self.toggle:
            self.state = not self.state

        if self.callback:
            self.refresh = self.callback(self)
        else:
            self.refresh = True

        if self.refresh:
            self.parent.update()

    def update(self):
        if self.refresh:
            self.refresh = False
            self.draw()
            return True
