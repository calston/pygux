import pygame
import time
import math

from pygame.locals import *
from pygux.colours import Colours

def hlBox(surface, x, y, w, h, c1=Colours.white, c2=Colours.black):
    pygame.draw.line(surface, c1, (x, h), (x, y))
    pygame.draw.line(surface, c1, (x, y), (w, y))
    pygame.draw.line(surface, c2, (w, y), (w, h))
    pygame.draw.line(surface, c2, (w, h), (x, h))

class Widget(object):
    touch = False
    def __init__(self, x, y, w=1, h=1, display=None, parent=None):
        self.x, self.y = x, y
        self.w, self.h = w, h

        self.parent = parent
        self.display = display

        self.refresh = False

    def update(self):
        # Called on every display loop - must return True if re-render required
        if self.refresh:
            self.refresh = False
            self.draw()
            return True

    def draw(self):
        # Draw the initial widget
        pass

    def inside(self, pos):
        x, y = pos
        if (x >= self.x) and (x <= (self.x + self.w)):
            if (y >= self.y) and (y <= (self.y + self.h)):
                return True
        return False

    def touched(self, position):
        return False

class Text(Widget):
    touch = True
    def __init__(self, text, x, y, w, h, align=0, txt_col=Colours.pale_blue,
                 bg_colour=Colours.white, font=None, **kw):
        """Button widget
        """
        Widget.__init__(self, x, y, w, h, **kw)

        self.text = text
        self.txt_col = txt_col
        self.align = align

        self.bg_colour = bg_colour

        if not font:
            self.font = self.display.font
        else:
            self.font = font

    def setText(self, text):
        self.text = text
        self.refresh = True

    def draw(self):
        surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        surface.fill(self.bg_colour)

        btText = self.font.render(self.text, True, self.txt_col)

        tw, th = self.font.size(self.text)
        ty = (self.h / 2) - (th / 2)

        if self.align == 0:
            tx = (self.w / 2) - (tw / 2)
        else:
            tx = 0

        surface.blit(btText, (tx, ty))
       
        self.parent.surface.blit(surface, (self.x, self.y))



