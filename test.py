import pygame

from pygux import Application, Colours, fa
from pygux import fa
from pygux.widgets import Panel, Button, Sprite
from pygux.display import Display

class TestApp(Application):
    def create_sidebar(self):
        self.sidebar = Panel(0, 0, 32, 128, self)

        fontawesome = pygame.font.Font('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 10)

        buttons = [
            (fa.FA_AREA_CHART, None),
            (fa.FA_SUPERSCRIPT, None),
            (fa.FA_COG, None),
        ]

        for i, b in enumerate(buttons):
            f, c = b
            self.sidebar.addWidget(Button, f, 0, i*24, 32, 24,
                                    font=fontawesome, toggle=True,
                                    callback=c)
        self.sidebar.draw()

    def keyDown(self, event):
        if event.key == 113:
            self.stop()

    def updateFrames(self):
        self.sidebar.update()
        self.main.update()

    def initializeVideo(self):
        self.display = Display(h=128, w=128)

        self.create_sidebar()

        self.main = Panel(32, 0, 96, 128, self)
        self.main.addWidget(Sprite, 0, 0, 64, 64, "bird1_after.jpg")
        self.main.draw()

        self.display.flip()


if __name__ == '__main__':

    app = TestApp()
    app.start()
