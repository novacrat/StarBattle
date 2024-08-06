import random, pygame, pygame.gfxdraw
from engine.animation import Animation, Transition
from views.debugger import theDebugger
from engine import View, theViewer


COLOR_VOID = 0, 0, 0
COLOR_MAIN = 7, 23, 55
ANI_FADE_IN = Animation(color=COLOR_MAIN, duration=2.5, transition=Transition.easeOutSine)
ANI_FADE_OUT = Animation(color=COLOR_VOID, duration=0.5, transition=Transition.easeOutSine)


class Stars(View):
    visible = True
    progressive = True
    color = COLOR_VOID

    def __init__(self, amount=150):
        self._width = theViewer.screen.get_width()
        self._height = theViewer.screen.get_height()
        self.stars = [[
            random.uniform(0, self._width),
            random.uniform(0, self._height),
            random.uniform(7, 50),  # speed
            (200, 200, random.randint(200, 255), 125)  # color
        ] for i in range(amount)]

    def fade_in(self):
        self.animate(ANI_FADE_IN)

    def fade_out(self):
        self.animate(ANI_FADE_OUT)

    def _progress(self, dt):
        for i in range(len(self.stars)):
            self.stars[i][0] += self.stars[i][2] * dt
            if self.stars[i][0] > self._width:
                self.stars[i][0] -= self._width
                self.stars[i][1] = random.randint(0, self._height)

    def _draw(self, srf: pygame.SurfaceType):
        srf.lock()
        srf.fill(self.color)
        for star in self.stars:
            pygame.draw.aaline(srf, star[3], (star[0], star[1]), (star[0], star[1]))
            # srf.set_at((int(star[0]), int(star[1])), star[3])
        srf.unlock()



