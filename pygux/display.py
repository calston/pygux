import pygame, sys, os
from pygame.locals import *

from pygux.widgets.colours import Colours

class Display(object):
    def __init__(self, bg_colour=Colours.black, font_size=12, w=800, h=480,
                 font="/usr/share/fonts/truetype/freefont/FreeSans.ttf"):
        pygame.init()

        self.display = pygame.display.set_mode((w, h), pygame.HWSURFACE, 24)

        self.w = 800
        self.h = 480

        self.display.fill(Colours.white)

        self.font = pygame.font.Font(font, font_size)

    def splash(self):
        self.splash = pygame.image.load('images/pi_black_glow2.png').convert()

        self.blit(self.splash, (0,0))
        pygame.display.update()

    def surface(self, w, h, cmap=pygame.SRCALPHA):
        return pygame.Surface((w, h), cmap)

    def rect(self, x, y, w, h, c, fill=1):
        pygame.draw.rect(self.display, c, (x, y, w, h), fill)

    def clear(self):
        self.display.fill((0,0,0))

    def blit(self, *a, **kw):
        self.display.blit(*a, **kw)

    def flip(self):
        pygame.display.flip()

class TouchScreen(Display):
    def __init__(self, fbdev='/dev/fb0', tsdev='/dev/input/touchscreen', **kw):
        os.environ["SDL_FBDEV"] = fbdev
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        os.environ["SDL_MOUSEDEV"] = tsdev
        os.environ["TSLIB_CALIBFILE"] = "/etc/pointercal"
        os.environ["TSLIB_FBDEVICE"] = fbdev
        os.environ["TSLIB_TSDEVICE"] = tsdev

        Display.__init__(self, **kw)

        pygame.mouse.set_visible(0)

class Screen(Display):
    def __init__(self, fbdev='/dev/fb1', tsdev='/dev/input/touchscreen', **kw):
        os.environ["SDL_FBDEV"] = fbdev

        Display.__init__(self, **kw)

        pygame.mouse.set_visible(0)

