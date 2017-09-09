import pygame
import time
import math

from pygame.locals import *

class Colours(object):
    # A bunch of random colours

    white = (255, 255, 255)
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

class Panel(object):
    def __init__(self, x, y, w, h, core):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.widgets = []
        self.core = core
        self.display = core.display
        self.debounce = 0
        self.debounce_time = 5

        self.bg_colour = Colours.pale_blue

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
            now = time.time() * 1000
            if (now - self.debounce) < self.debounce_time:
                return False

            for w in reversed(self.widgets):
                if w.touch and w.inside(newpos):
                    w.touched()
                    break

    def mouseUp(self, event):
        self.debounce = 0
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
            self.display.blit(self.surface, (self.x, self.y))
            self.display.flip()

class Widget(object):
    touch = False
    def __init__(self, x, y, w=1, h=1, display=None, parent=None):
        self.x, self.y = x, y
        self.w, self.h = w, h

        self.parent = parent
        self.display = display

    def update(self):
        # Called on every display loop - must return True if re-render required
        return False

    def draw(self):
        # Draw the initial widget
        pass

    def inside(self, pos):
        x, y = pos
        if (x >= self.x) and (x <= (self.x + self.w)):
            if (y >= self.y) and (y <= (self.y + self.h)):
                return True
        return False

    def touched(self):
        return False

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

    def touched(self):
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
                 toggle_txt_col=Colours.black, txt_col=Colours.white,
                 bg_colour=Colours.pale_blue, font=None, **kw):
        Widget.__init__(self, x, y, w, h, **kw)
        self.text = text
        self.callback = callback
        self.bg_colour = bg_colour
        self.toggle_colour = toggle_colour
        if toggle_text:
            self.toggle_text = toggle_text
        else:
            self.toggle_text = self.text
        self.toggle = toggle

        self.txt_col = txt_col
        self.toggle_txt_col = toggle_txt_col

        self.state = 0
        self.refresh = False

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
       
        pygame.draw.line(surface, c1, (0, self.h-1), (0, 0))
        pygame.draw.line(surface, c1, (0, 0), (self.w-1, 0))

        pygame.draw.line(surface, c2, (self.w-1, 0), (self.w-1, self.h-1))
        pygame.draw.line(surface, c2, (self.w-1, self.h-1), (0, self.h-1))

        self.parent.surface.blit(surface, (self.x, self.y))

    def touched(self):
        if self.toggle:
            self.state = not self.state

        if self.callback:
            self.refresh = self.callback(self)
        else:
            self.refresh = True

        self.parent.update() # Force parent update so callback doesn't block redraw

    def update(self):
        if self.refresh:
            self.refresh = False
            self.draw()
            return True
