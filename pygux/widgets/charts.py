import pygame
import math

from pygame.locals import *
from pygux.widgets.widget import Widget
from pygux.colours import Colours

class Chart(Widget):
    touch = True
    def __init__(self, x, y, w, h, bg_colour=Colours.white, agr_fn=lambda l: max(l), **kw):
        """Chart widget
        """
        Widget.__init__(self, x, y, w, h, **kw)

        self.bg_colour = bg_colour

        self.major_ticks = 10
        self.x_ticks = [str(i) for i in range(self.major_ticks)]
        self.y_ticks = []

        self.data = []
        self.scale = 1.0
        self.aggregation = agr_fn

    def _scale_y(self, height, val):
        return val * self.scale * height

    def updateData(self, data, x_max=None, x_min=0, y_min=0, y_max=None):
        num_recs = len(data)
        self.y_min, self.y_max = y_min, y_max
        self.x_max, self.x_min = x_max, x_min

        self.scale = self.h / float(self.y_max - self.y_min)

        self.x_ticks = []
        for i in range(self.major_ticks):
            val = self.x_min + (i * (self.x_max - self.x_min))
            v = "%d" % val
            if len(v) > 9:
                v = "%dG" % (val/1000000000)
            if len(v) > 6:
                v = "%dM" % (val/1000000)
            if len(v) > 3:
                v = "%dK" % (val/1000)
            self.x_ticks.append(v)

        if num_recs < self.w:
            spacing = int(self.w / num_recs)
            self.data = [(i * spacing, int((v - self.y_min) * self.scale))
                         for i, v in enumerate(data)]

        elif num_recs == self.w:
            self.data = [(i, int((v - self.y_min) * self.scale))
                         for i, v in enumerate(data)]

        else:
            self.data = []
            
            # Group samples into buckets averaged over the number of pixels
            comp = int(num_recs / self.w)
            tdata = [data[i:i + comp]
                     for i in xrange(0, len(data), comp)]

            for i, v in enumerate(tdata):
                newv = int((self.aggregation(v) - self.y_min) * self.scale)

                self.data.append((i, newv))

        self.refresh = True
            
    def draw(self):
        surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        surface.fill(self.bg_colour)

        half_h = (self.h/2)
        half_w = (self.w/2)

        axis_col = (0,0,0)
        # Outside box
        hlBox(surface, 0, 0, self.w - 1, self.h - 1, axis_col, axis_col)

        # Major ticks
        major_col = (150, 150, 150)
        gap = self.w/10

        tick_font = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)

        for i in range(10):
            x = gap * (i + 1)
            pygame.draw.line(surface, major_col, (x, 0), (x, self.h))

            text = tick_font.render(self.x_ticks[i], True, Colours.black)
            surface.blit(text, (x, self.h - 25))


        numy = int(self.h / gap)
        for i in range(numy):
            y = gap * (i + 1)
            pygame.draw.line(surface, major_col, (0, self.h - y), (self.w, self.h - y))

        c1 = Colours.blue

        # Plot the lines
        for i, d in enumerate(self.data):
            if i > 0:
                x1, y1 = self.data[i-1]
                x2, y2 = d

                # Y is inverted when plotting
                pygame.draw.line(
                    surface,
                    c1,
                    (x1, self.h - y1),
                    (x2, self.h - y2),
                    3
                )

        self.parent.surface.blit(surface, (self.x, self.y))

class Scope(Widget):
    touch = True
    def __init__(self, x, y, w, h, bg_colour=Colours.white, scale=1.0, agr_fn=lambda l: sum(l)/float(len(l)), **kw):
        """Scope widget
        """
        Widget.__init__(self, x, y, w, h, **kw)

        self.bg_colour = bg_colour

        self.data = []

        # Starting timebase (miliseconds)
        self.timebase = 0.001
        self.scale = float(scale)
        self.aggregation = agr_fn
        self.raw_data = []

        self.more_data = False

        self.grid = self.construct_grid()

    def construct_grid(self):
        surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        axis_col = (0,0,0)

        half_h = (self.h/2)
        half_w = (self.w/2)
        # Outside box
        hlBox(surface, 0, 0, self.w - 1, self.h - 1, axis_col, axis_col)

        # Center cross
        pygame.draw.line(surface, axis_col, (half_w, 0), (half_w, self.h))
        pygame.draw.line(surface, axis_col, (0, half_h), (self.w, half_h))

        # Major ticks
        major_col = (150, 150, 150)
        gap = self.w/10
        for i in range(4):
            x = gap * (i + 1)
            pygame.draw.line(surface, major_col, (half_w + x, 0), (half_w + x, self.h))
            pygame.draw.line(surface, major_col, (half_w - x, 0), (half_w - x, self.h))

        numy = int(half_h / gap)
        for i in range(numy):
            y = gap * (i + 1)
            pygame.draw.line(surface, major_col, (0, half_h + y), (self.w, half_h + y))
            pygame.draw.line(surface, major_col, (0, half_h - y), (self.w, half_h - y))

        return surface

    def _scale_y(self, height, val):
        return val * self.scale * height

    def updateData(self, data, time_step):
        half_h = (self.h/2) - 1
        maxtime = self.timebase * 10
        samples = 1 + int(maxtime / time_step)
        self.data = []

        if samples < len(data):
            data = data[:samples]

        if samples > len(data):
            print "Increase decimation"
            return 

        if samples > self.w:
            comp = int(math.ceil(samples / float(self.w)))

            tdata = [data[i:i + comp]
                 for i in xrange(0, len(data), comp)]

            for i, v in enumerate(tdata):
                newv = int((self.aggregation(v) / self.scale) * half_h)
                self.data.append((i, newv))
        else:
            xstep = self.w / float(samples)
            self.data = [(int(i * xstep), int((v / self.scale) * half_h)) for i, v in enumerate(data)]

        self.refresh = True

    def draw(self):
        surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        surface.fill(self.bg_colour)

        surface.blit(self.grid, (0,0))

        half_h = (self.h/2)
        half_w = (self.w/2)

        c1 = Colours.blue

        # Plot the lines
        for i, d in enumerate(self.data):
            if i > 0:
                x2, y2 = d
                x1, y1 = self.data[i - 1]

                # Y is inverted when plotting
                pygame.draw.line(
                    surface,
                    c1,
                    (x1, half_h - y1),
                    (x2, half_h - y2),
                    3
                )

        self.parent.surface.blit(surface, (self.x, self.y))

