import pygame
import time
import math

from pygame.locals import *

class Colours(object):
    # A bunch of random colours

    #white = (255, 255, 255)
    white = (192, 192, 192)
    very_light_gray = (192, 192, 192)
    light_gray = (128, 128, 128)
    med_gray = (64, 64, 64)
    gray = (32, 32, 32)
    black = (0, 0, 0)

    sepia = (120, 100, 82)

    red = (200, 17, 55)
    yellow = (255, 255, 81)
    green = (44, 160, 90)

    blue = (0, 0, 255)
    electric_blue = (0, 191, 255)
    pale_blue = (0, 131, 235)
    dark_pale_blue = (0, 101, 205)

def hlBox(surface, x, y, w, h, c1=Colours.white, c2=Colours.black):
    pygame.draw.line(surface, c1, (x, h), (x, y))
    pygame.draw.line(surface, c1, (x, y), (w, y))
    pygame.draw.line(surface, c2, (w, y), (w, h))
    pygame.draw.line(surface, c2, (w, h), (x, h))

class Panel(object):
    def __init__(self, x, y, w, h, core, bg_colour=Colours.pale_blue):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.widgets = []
        self.core = core
        self.display = core.display

        self.bg_colour = bg_colour

        self.surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        self.core.registerHandler(MOUSEBUTTONDOWN, self.mouseDown)
        self.core.registerHandler(MOUSEBUTTONUP, self.mouseUp)

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


class SevenSegment(Widget):
    charMap = {
        '0': (True,  True,  True,  True,  True,  True,  False),
        '1': (False, True,  True,  False, False, False, False),
        '2': (True,  True,  False, True,  True,  False, True),
        '3': (True,  True,  True,  True,  False, False, True),
        '4': (False, True,  True,  False, False, True,  True),
        '5': (True,  False, True,  True,  False, True,  True),
        '6': (True,  False, True,  True,  True,  True,  True),
        '7': (True,  True,  True,  False, False, False, False),
        '8': (True,  True,  True,  True,  True,  True,  True),
        '9': (True,  True,  True,  False, False, True,  True)
    }

    def __init__(self, x, y, w, h, value=0, digits=2, msd=1, colour=Colours.red, digit_pad=5, **kw):
        Widget.__init__(self, x, y, w, h, **kw)

        self.digits = digits
        self.colour = colour
        self.lastV = self.value = value
        self.digit_pad = digit_pad
        self.msd = msd

        self.constructSurface()

    def constructSurface(self):
        self.digit = pygame.Surface((self.w, self.h))
        
        self.dw = int((self.w / self.digits) - self.digit_pad)

        dh = (self.h / 2) - self.digit_pad

        # Horizontal segment
        self.h_dark = pygame.Surface((self.dw - 10, 10), pygame.SRCALPHA)
        self.h_light = pygame.Surface((self.dw - 10, 10), pygame.SRCALPHA)

        h_shape = [
            (0, 5),
            (5, 0),
            (self.dw - 15, 0),
            (self.dw - 10, 5),
            (self.dw - 15, 10),
            (5, 10)
        ]
        pygame.draw.polygon(self.h_dark, Colours.gray, h_shape)
        pygame.draw.polygon(self.h_light, self.colour, h_shape)

        self.v_dark = pygame.Surface((10, dh), pygame.SRCALPHA)
        self.v_light = pygame.Surface((10, dh), pygame.SRCALPHA)

        v_shape = [
            (5, 0),
            (10, 5),
            (10, dh - 15),
            (5, dh - 10),
            (0, dh - 15),
            (0, 5),
        ]
        pygame.draw.polygon(self.v_dark, Colours.gray, v_shape)
        pygame.draw.polygon(self.v_light, self.colour, v_shape)

        for i in range(self.digits):
            x = (self.dw + self.digit_pad) * i

            # Horizontal segments
            self.digit.blit(self.h_dark, (x+5, 0))
            self.digit.blit(self.h_dark, (x+5, (self.h/2) - 5))
            self.digit.blit(self.h_dark, (x+5, self.h - 10))

            # Vertical segments
            self.digit.blit(self.v_dark, (x, 10))
            self.digit.blit(self.v_dark, (x+self.dw-10, 10))
            self.digit.blit(self.v_dark, (x, 5+self.h/2))
            self.digit.blit(self.v_dark, (x+self.dw-10, 5+self.h/2))

    def lightSegments(self):
        panel = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        dst = (self.h_dark, self.h_light, self.v_dark, self.v_light)

        v = "%f" % self.value
        nd = len(v.split('.')[0])
        if nd < self.msd:
            v = '0'*(self.msd - nd) + v

        cn = 0
            
        for c in v:
            if cn >= self.digits:
                break

            if (c == '.') and (cn <= self.digits):
                pygame.draw.circle(panel, self.colour, (x + self.dw + 2, self.h-5), 5)
                continue

            if c in self.charMap:
                x = (self.dw + self.digit_pad) * cn
                cn += 1
                segments = [
                    (0, (x+5, 0)),
                    (2, (x+self.dw-10, 10)),
                    (2, (x+self.dw-10, 5 + self.h/2)),
                    (0, (x+5, self.h - 10)),
                    (2, (x, 5+self.h/2)),
                    (2, (x, 10)),
                    (0, (x+5, (self.h/2) - 5)),
                ]

                for i, s in enumerate(self.charMap[c]):
                    if s:
                        args = (dst[segments[i][0] + 1], segments[i][1])
                    else:
                        args = (dst[segments[i][0]], segments[i][1])

                    panel.blit(*args)

        return panel

    def draw(self):
        x, y = self.getXY()
        if self.digit:
            self.display.blit(self.digit, (x, y))
            self.display.blit(self.lightSegments(), (x, y))

    def update(self):
        if self.value != self.lastV:
            self.draw()
            self.lastV = self.value
            return True

class FancyGauge(Widget):
    def __init__(self, x, y, r, showPercentage = False, valueFormat = "%d",
                 colour=Colours.green, units = None, maxScale = 25,
                 touched=None, **kw):
        Widget.__init__(self, x, y, **kw)
        self.r = r
        self.h = self.w = (2 * r) + 2

        self.value = 0
        self.lastV = self.value
        self.valueFormat = valueFormat
        self.showPercentage = showPercentage

        self.colour = colour
        self.units = units
        self.maxScale = maxScale

        self.callback = touched

        self.constructSurface()

    def constructSurface(self):
        self.meter = pygame.Surface((self.h, self.w))

        pygame.draw.circle(self.meter, Colours.gray, (int(self.w/2), int(self.h/2)), self.r, int(self.r*0.25))

        self.valueFont = pygame.font.Font('carlito.ttf', int(self.r*0.5))

        if self.units:
            unitFont = pygame.font.Font('carlito.ttf', int(self.r*0.30))
            w, h = unitFont.size(self.units)
            units = unitFont.render(self.units, True, Colours.light_gray)
            self.meter.blit(units, ((self.w / 2) - (w/2), ((self.h/2) - (h/2)) + h))

    def arcSlice(self, center, rad1, rad2, angle):
        arc1 = []
        arc2 = []
        pi = math.pi
        for n in range(-90,angle-90):
            # Trig is expensive, do it once.
            cs = math.cos(n*pi/180)
            ss = math.sin(n*pi/180)
            
            arc1.append((center[0] + int(rad1 * cs), center[1] + int(rad1 * ss)))
            arc2.insert(0, (center[0] + int(rad2 * cs), center[1] + int(rad2 * ss)))

        if not arc1:
            return []

        arc2.extend(arc1[0])
        arc1.extend(arc2)
        return arc1

    def draw(self):
        submeter = pygame.Surface((self.h, self.w))
        submeter.blit(self.meter, (0,0))

        # Draw value text
        pv = self.value / self.maxScale
        if pv > 1:
            pv = 1

        if self.showPercentage:
            vt = "%d%%" % int(pv*100)
        else:
            vt = self.valueFormat % self.value
            
        w, h = self.valueFont.size(vt)
        val = self.valueFont.render(vt, True, self.colour)

        submeter.blit(val, ((self.w / 2) - (w/2), (self.h/2) - (h/2) - 5))


        # Draw the value arc
        if (pv > 0):
            sm2 = pygame.Surface((self.h, self.w), pygame.SRCALPHA)
            arcSliceD = int(math.ceil(360 * pv))
            poly = self.arcSlice((int(self.w/2), int(self.h/2)), self.r, self.r*0.75, arcSliceD)
            if poly:
                pygame.draw.polygon(sm2, self.colour, poly)
                submeter.blit(sm2, (0, 0))
        x, y = self.getXY()
        self.display.blit(submeter, (x, y))

    def update(self):
        if (self.value != self.lastV) and (self.value <= self.maxScale):
            self.draw()
            self.lastV = self.value
            return True

    def touched(self, position):
        if self.callback:
            self.callback()

class OldSchoolMeter(Widget):
    def __init__(self, x, y, maxScale = 25, **kw):
        Widget.__init__(self, x, y, **kw)
        self.h, self.w = 100, 146
        self.maxScale = maxScale
        self.value = 0
        self.lastV = self.value
        self.constructSurface()

    def constructSurface(self):
        self.meter = pygame.image.load('images/meter-bg.png').convert()
        font = pygame.font.Font('carlito.ttf', 12)
        # Calculate the increment between text
        segments = math.ceil(self.maxScale / 6.0)

        r = 60.0

        # Render display markings
        for i in range(6):
            text = font.render(str(i*segments), True, Colours.sepia) 

            a = float(50.0 - (i * 20.0))

            text = pygame.transform.rotate(text, a)

            aR = (a+90) * (math.pi / 180.0)

            self.meter.blit(text, (67 + int(math.cos(aR) * (r*1.05)), 92 - int(math.sin(aR) * r)))

    def update(self):
        if self.value != self.lastV:
            self.draw()
            self.lastV = self.value
            return True

    def draw(self):
        surf = pygame.Surface((self.w, self.h))

        surf.blit(self.meter, (0, 0))

        r1 = 70.0
        r2 = 10.0

        aR = (140 - ((self.value / self.maxScale) * 107)) * (math.pi / 180.0)

        pygame.draw.aaline(surf, (43, 28, 18), 
            (72 + int(math.cos(aR) * (r1*1.05)), 92 - int(math.sin(aR) * r1)),
            (72 + int(math.cos(aR) * (r2*1.05)), 92 - int(math.sin(aR) * r2)),
        )
        x, y = self.getXY()
        self.display.blit(surf, (x, y))

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

        if toggle_text:
            self.toggle_text = toggle_text
        else:
            self.toggle_text = self.text

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
            btText = self.font.render(self.toggle_text, True, self.toggle_txt_col)
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

class Scope(Widget):
    touch = True
    def __init__(self, x, y, w, h, bg_colour=Colours.white, scale=1.0, agr_fn=lambda l: max(l), **kw):
        """Scope widget
        """
        Widget.__init__(self, x, y, w, h, **kw)

        self.bg_colour = bg_colour

        self.data = []
        self.scale = float(scale)
        self.aggregation = agr_fn

    def _scale_y(self, height, val):
        return val * self.scale * height

    def updateData(self, data):
        recs = len(data)

        half_h = (self.h/2) - 1

        if recs < self.w:
            spacing = int(self.w / recs)
            self.data = [(i * spacing, (v / self.scale) * half_h) 
                         for i, v in enumerate(data)]

        elif recs == self.w:
            self.data = [(i, (v / self.scale) * half_h)
                         for i, v in enumerate(data)]

        else:
            self.data = []
            
            # Group samples into buckets averaged over the number of pixels
            compression = int(recs / self.w)
            tdata = [data[i:i + compression]
                     for i in xrange(0, len(data), compression)]

            for i, v in enumerate(tdata):
                newv = int((self.aggregation(v) / self.scale) * half_h)

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
                    (x1, half_h - y1),
                    (x2, half_h - y2)
                )

        self.parent.surface.blit(surface, (self.x, self.y))

class Dropdown(Widget):
    touch = True
    def __init__(self, x, y, w, h, align=0, txt_col=Colours.white, items=[],
                 default=0, bg_colour=Colours.pale_blue, font=None, **kw):
        """Dropdown widget
        """
        Widget.__init__(self, x, y, w, h, **kw)

        self.txt_col = txt_col
        self.align = align

        self.default = default

        self.bg_colour = bg_colour

        self.popped = False

        self.items = items

        if not font:
            self.font = self.display.font
        else:
            self.font = font

    def touched(self, p):
        if self.popped:
            self.popped = False
        else:
            self.popped = True

        self.refresh = True
        self.parent.update() 

    def draw(self):
        surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        dtext = self.items[self.default]
        surface.fill(self.bg_colour)
        btText = self.font.render(dtext, True, self.txt_col)

        tw, th = self.font.size(dtext)
        tx = (self.w / 2) - (tw / 2)
        ty = (self.h / 2) - (th / 2)

        surface.blit(btText, (tx, ty))

        if self.popped:
            c1 = Colours.white
            c2 = Colours.black
            item_count = len(self.items)

            popout = pygame.Surface((self.w, self.h * item_count), pygame.SRCALPHA)

            hlBox(surface, 0, 0, self.w, self.h * item_count, c2, c1)

            self.parent.surface.blit(surface, (self.x, self.y))

        else:
            c1 = Colours.white
            c2 = Colours.black

        hlBox(surface, 0, 0, self.w - 1, self.h - 1, c1, c2)

        self.parent.surface.blit(surface, (self.x, self.y))

