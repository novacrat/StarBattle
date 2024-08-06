import pygame
from engine.viewer import View


class Debugger(View):
    _SHOW_MSGS = False

    def __init__(self):
        pygame.font.init()
        self.debug_font = pygame.font.Font('fonts/Orbitron Light.otf', 13)
        self.messages = list()
        pass

    def draw(self, srf: pygame.SurfaceType):
        global app
        if self._SHOW_MSGS:
            for i, msg in enumerate(self.messages):
                text = self.debug_font.render(msg, True, (255, 255, 255))
                srf.blit(text, (srf.get_width() - text.get_width() - 20, 20 + 16 * i))

theDebugger = Debugger()