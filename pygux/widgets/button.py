import pygame
import time
import math

from pygame.locals import *

from pygux.widgets.widget import Widget, hlBox
from pygux.colours import Colours


class Button(Widget):
    touch = True
    def __init__(self, text, x, y, w, h, callback=None, toggle=False,
                 toggle_text=None, toggle_colour=Colours.dark_pale_blue,
                 toggle_txt_col=Colours.black, txt_col=Colours.white, state=False,
                 bg_colour=Colours.pale_blue, font=None, **kw):
        """Button widget
        """
        Widget.__init__(self, x, y, w, h, **kw)

        self.state = state

        self.text = text
        self.txt_col = txt_col

        self.callback = callback
        self.bg_colour = bg_colour

        self.toggle = toggle
        self.toggle_colour = toggle_colour

        self.toggle_text = toggle_text

        self.toggle_txt_col = toggle_txt_col

        if not font:
            self.font = self.display.font
        else:
            self.font = font

    def draw(self):
        surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        if self.state == 0:
            surface.fill(self.bg_colour)
            btText = self.font.render(self.text, True, self.txt_col)
            c1 = Colours.white
            c2 = Colours.black
        else:
            surface.fill(self.toggle_colour)
            if self.toggle_text:
                btText = self.font.render(self.toggle_text, True, self.toggle_txt_col)
            else:
                btText = self.font.render(self.text, True, self.toggle_txt_col)
            c1 = Colours.black
            c2 = Colours.white

        tw, th = self.font.size(self.text)
        tx = (self.w / 2) - (tw / 2)
        ty = (self.h / 2) - (th / 2)

        surface.blit(btText, (tx, ty))
       
        hlBox(surface, 0, 0, self.w - 1, self.h - 1, c1, c2)

        self.parent.surface.blit(surface, (self.x, self.y))

    def touched(self, position):
        if self.toggle:
            self.state = not self.state

        if self.callback:
            self.refresh = self.callback(self)
        else:
            self.refresh = True

        if self.refresh:
            self.parent.update() # Force parent update so callback doesn't block redraw

    def update(self):
        if self.refresh:
            self.refresh = False
            self.draw()
            return True

class ButtonGroup(Widget):
    touch = True
    def __init__(self, items, x, y, w, h, callback=None, vertical=True,
                 toggle_colour=Colours.dark_pale_blue,
                 toggle_txt_col=Colours.black,
                 txt_col=Colours.white,
                 bg_colour=Colours.pale_blue, **kw):

        """Group of buttons
        """
        Widget.__init__(self, x, y, w, h, **kw)

        self.bg_colour = bg_colour
        self.txt_col = txt_col
        self.toggle_colour = toggle_colour
        self.toggle_txt_col = toggle_txt_col

        self.vertical = vertical

        self.items = self.construct(items)

    def construct(self, items):
        self.surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        item_set = []

        num_items = len(items)

        if self.vertical:
            x_step = 0
            y_step = self.h / num_items
            w = self.w
            h = y_step - 1
        else:
            x_step = self.w / num_items
            y_step = 0
            w = x_step - 1
            h = self.h

        for i, item in enumerate(items):
            text = item.pop('text')
            btn = Button(text, x_step * i, y_step * i, w, h, **item)
            btn.display = self.display
            btn.parent = self
            btn.index = i

            item_set.append(btn)

        return item_set

    def draw(self):
        for btn in self.items:
            btn.draw()

        self.parent.surface.blit(self.surface, (self.x, self.y))

    def touched(self, p):
        position = (p[0] - self.x, p[1] - self.y)
        for item in self.items:
            if item.touch and item.inside(position):
                item.touched(position)

        return True
                    
    def update(self):
        fl = False
        for item in self.items:
            r = item.update()
            fl = fl or r
        
        if fl:
            self.draw()
            self.parent.redraw()

        return fl


class Dropdown(Widget):
    touch = True
    def __init__(self, x, y, w, h, align=0, txt_col=Colours.white, items=[], callback=None,
                 default=0, bg_colour=Colours.pale_blue, font=None, **kw):
        """Dropdown widget
        """
        Widget.__init__(self, x, y, w, h, **kw)

        self.orig = (x, y, w, h)

        self.txt_col = txt_col
        self.align = align
        self.bg_colour = bg_colour

        self.popped = False
        self.skip_draw = False

        self.selected = default

        if not font:
            self.font = self.display.font
        else:
            self.font = font

        self.callback = callback

        self.set_items(items)

    def set_items(self, items):
        self.items = []
        for index, item in enumerate(items):
            # Calculate dimensions once to speed up rendering a bit
            y = index * self.h
            btText = self.font.render(item, True, self.txt_col)
            tw, th = self.font.size(item)
            tx = (self.w / 2) - (tw / 2)
            ty = (self.h / 2) - (th / 2)

            self.items.append((
                item,
                btText,
                (1, 1 + y, self.w - 2, self.h - 1),
                (1 + tx, 1 + ty + y),
            ))

    def inside_inside(self, pos, box):
        x, y = pos
        if (x >= box[0]) and (x <= (box[0] + box[2])):
            if (y >= box[1]) and (y <= (box[1] + box[3])):
                return True
        return False

    def touched(self, p):
        if self.popped:
            if p[0] > self.orig[2]:
                poppos = (p[0] - self.orig[2] - self.orig[0], p[1] - self.orig[1])

                for index, item in enumerate(self.items):
                    if self.inside_inside(poppos, item[2]):
                        self.selected = index
                        self.callback(self.selected)

            self.popped = False
        else:
            self.popped = True
            self.w = self.orig[2] * 2
            self.h = self.orig[3] * len(self.items)

        self.refresh = True
        self.parent.update() 

    def draw(self):
        if self.skip_draw:
            return
        x, y, w, h = self.orig
        surface = pygame.Surface((w, h), pygame.SRCALPHA)

        surface.fill(self.bg_colour)

        dtext = self.items[self.selected][0]
        btText = self.font.render(dtext, True, self.txt_col)

        tw, th = self.font.size(dtext)
        tx = (w / 2) - (tw / 2)
        ty = (h / 2) - (th / 2)

        surface.blit(btText, (tx, ty))

        if self.popped:
            c1 = Colours.white
            c2 = Colours.black
            item_count = len(self.items)

            popout = pygame.Surface((1 + w, 1 + (h * item_count)), pygame.SRCALPHA)
            popout.fill(self.bg_colour)
            hlBox(popout, 0, 0, w, h * item_count, c2, c1)

            for index, item in enumerate(self.items):
                item, text, box, font_pos = item
                hlBox(popout, *box, c1=c1, c2=c2)
                popout.blit(text, font_pos)

            self.parent.surface.blit(popout,
                (x + w, y))

        else:
            c1 = Colours.white
            c2 = Colours.black
            self.skip_draw = True
            self.parent.draw()
            self.skip_draw = False

        hlBox(surface, 0, 0, w - 1, h - 1, c1, c2)

        self.parent.surface.blit(surface, (x, y))

