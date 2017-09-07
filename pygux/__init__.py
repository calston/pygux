import pygame

from pygame.locals import *

from pygux import display

from pygux.widgets import Colours
from pygux import widgets 
from pygux import fa


class Application(object):
    freq = 25

    def __init__(self):
        self.terminated = False
        self.clock = pygame.time.Clock()

        self.currentView = None

        self.eventHandlers = {
            QUIT: [self.stop],
            KEYDOWN: [self.keyDown],
            MOUSEBUTTONUP: [self.mouseUp],
            MOUSEBUTTONDOWN: [self.mouseDown]
        }

    def processEvents(self):
        for event in pygame.event.get():
            if event.type in [MOUSEBUTTONUP, MOUSEBUTTONDOWN]:
                if event.button != 1:
                    continue

            handlers = self.eventHandlers.get(event.type, [])

            for handler in handlers:
                handler(event)

    def registerHandler(self, evtype, callback):
        if evtype in self.eventHandlers:
            self.eventHandlers[evtype].append(callback)
        else:
            self.eventHandlers[evtype] = [callback]

    def frame(self):
        """Called for each clock tick"""
        pass

    def mainLoop(self):
        while not self.terminated:
            self.clock.tick(self.freq)
            self.processEvents()
            self.frame()

    def initializeVideo(self):
        self.display = display.TouchScreen()

    def start(self):
        self.initializeVideo()
        self.display.flip()
        self.mainLoop()

    def stop(self, event):
        self.terminated = True

    def keyDown(self, event):
        print event.key

    def mouseUp(self, event):
        #print "Done"
        pass

    def mouseDown(self, event):
        #print "Click"
        pass

