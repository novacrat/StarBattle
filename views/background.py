
import pygame
from engine.animation import Animation, Transition
from views.debugger import theDebugger
from engine import View, theViewer


COLOR_INITIAL = 0, 0, 0
COLOR_MENU = 7, 23, 55
# COLOR_MENU = 70, 130, 155


class Background(View):
    def __init__(self):
        self.color = COLOR_MENU
        self.ani = Animation(color=COLOR_INITIAL, duration=3, reverse=True)
        self.animate(self.ani)

    def draw(self, srf: pygame.SurfaceType):
        srf.fill(self.color)
