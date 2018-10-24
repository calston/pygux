import pygame
import time
import math

from pygame.locals import *
from pygux.colours import Colours


class Panel(object):
    def __init__(self, x, y, w, h, app, bg_colour=Colours.pale_blue):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.widgets = []
        self.app = app 
        self.display = app.display

        self.bg_colour = bg_colour

        self.surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        self.app.registerHandler(MOUSEBUTTONDOWN, self.mouseDown)
        self.app.registerHandler(MOUSEBUTTONUP, self.mouseUp)

    def addWidgetObj(self, widget):
        widget.parent = self
        widget.display = self.display
        self.widgets.append(widget)

    def addWidget(self, widgetClass, *args, **kw):
        kw['parent'] = self
        kw['display'] = self.display
        w = widgetClass(*args, **kw)
        self.widgets.append(w)
        return w

    def inside(self, pos):
        x, y = pos
        if (x >= self.x) and (x <= (self.x + self.w)):
            if (y >= self.y) and (y <= (self.y + self.h)):
                return True
        return False

    def mouseDown(self, event):
        if self.inside(event.pos):
            newpos = (event.pos[0] - self.x, event.pos[1] - self.y)

            for w in reversed(self.widgets):
                if w.touch and w.inside(newpos):
                    w.touched(newpos)
                    break

    def mouseUp(self, event):
        pass

    def draw(self):
        self.surface.fill(self.bg_colour)
        
        for w in self.widgets:
            w.draw()

        self.display.blit(self.surface, (self.x, self.y))

    def update(self):
        fl = False
        for w in self.widgets:
            r = w.update()
            fl = fl or r

        if fl:
            self.redraw()

    def redraw(self):
        self.display.blit(self.surface, (self.x, self.y))
        self.display.flip()


