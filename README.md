# pygux
Yet another Pygame UI library

You could use it like this
```python
import pygame

from pygux import Application, Colours
from pygux import widgets, fa
from pygux.display import TouchScreen

class TestApp(Application):
    def sidebar(self):
        self.sidebar = widgets.Panel(672, 0, 128, 480, self)

        fontawesome = pygame.font.Font('fontawesome-webfont.ttf', 70)

        buttons = [
            (fa.FA_AREA_CHART, None),
            (fa.FA_SUPERSCRIPT, None),
            (fa.FA_COG, None),
        ]

        for i, b in enumerate(buttons):
            f, c = b
            self.sidebar.addWidget(widgets.Button, f, 0, i*80, 128, 80,
                                    font=fontawesome, toggle=True,
                                    callback=c)

        bt = pygame.font.Font('bebasneue.ttf', 100)

        surf = bt.render("1234567890.00", True, Colours.pale_blue)

        self.display.blit(surf, (50, 50))

    def updateFrames(self):
        self.sidebar.update()

    def initializeVideo(self):
        self.display = TouchScreen()

        self.sidebar()
        self.sidebar.draw()


if __name__ == '__main__':

    app = TestApp()
    app.start()
```
