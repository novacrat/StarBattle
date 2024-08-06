
import pygame, pygame.gfxdraw
from engine.animation import Animation, Transition
from views.debugger import theDebugger
from engine import theViewer, View, Gradient


BOX_PADDING = 30

BOX_COLOR = 25, 0, 75, 128
TEXT_COLOR = 255, 255, 255

COUNT_COLOR = 235, 230, 255
COUNT_FADE_COLOR = 10, 117, 225
COUNT_SHIFT = 17.0


ANI_SHOW = Animation(
    opaque=1.0,
    duration=.15, transition=Transition.easeOutSine
)
ANI_HIDE = Animation(
    opaque=0.0, scale=3.0,
    duration=.25, transition=Transition.easeOutCubic
)

ANI_DIGIT_SHOW = Animation(
    opaque=1.0, ___shift=COUNT_SHIFT, shift=0.0,
    duration=.15, transition=Transition.easeOutSine
)
ANI_DIGIT_HIDE = Animation(
    opaque=0.0, shift=-COUNT_SHIFT, color=COUNT_FADE_COLOR,
    duration=.35, transition=Transition.easeOutSine
)
ANI_DIGIT_COLOR = Animation(
    ___color=COUNT_FADE_COLOR, color=COUNT_COLOR,
    duration=0.75, transition=Transition.easeOutQuad
)

DURATION = 3.05


class TransientMessage(View):
    visible = True
    progressive = True
    
    _DEFAULT_COUNT_INTERVAL = 1.0

    opaque = 0.0
    scale = 1.0

    def __init__(self, **kwargs):
        self.message = kwargs.pop('message')
        self.preamble = kwargs.pop('preamble', None)
        # counter
        self.count_items = list()
        self.count = kwargs.pop('count')
        if isinstance(self.count, (list, tuple)):
            self.count_items = self.count
            self.count = len(self.count_items)
        self.count_interval = kwargs.pop('count_interval', self._DEFAULT_COUNT_INTERVAL)
        self.count_t = 0.95 * self.count_interval
        self.count_show = kwargs.pop('count_show', False)
        self.count_views = list()
        # on complete function
        self.on_complete = kwargs.pop('on_complete', None)

        pos_y = BOX_PADDING

        if self.preamble:
            self.preamble_font = pygame.font.Font('fonts/Orbitron Medium.otf', 20)
            size = self.preamble_font.size(self.preamble)
            self.preamble = (self.preamble, size[0], pos_y)
            pos_y += self.preamble_font.get_linesize()

        self.message_font = pygame.font.Font('fonts/Orbitron Bold.otf', 36)
        size = self.message_font.size(self.message)
        self.message = (self.message, size[0], pos_y)
        pos_y += self.message_font.get_linesize()

        if self.count_show:
            self.counter_font = pygame.font.Font('fonts/Orbitron Black.otf', 70)
            self.counter_y = pos_y
            pos_y += self.counter_font.get_linesize()

        self.box_height = pos_y + BOX_PADDING

        self.box_color = BOX_COLOR

    def show(self):
        self.animate(ANI_SHOW)

    def hide(self):
        self.animate(ANI_HIDE & {'on_end': self.on_complete})
        self.visible = False

    def _draw(self, srf: pygame.SurfaceType):
        s_width, s_height = srf.get_size()

        # Box, adjusted with opaque
        s_box_width, s_box_height = s_width * 3 // 4, self.box_height
        s_box = pygame.Surface((s_box_width, s_box_height), pygame.SRCALPHA, 32)
        s_box.fill(list(self.box_color[0:3]) + [int(self.box_color[3] * self.opaque)])

        # Content
        s_message = self.message_font.render(self.message[0], True, TEXT_COLOR)
        s_box.blit(s_message, ((s_box_width - self.message[1]) // 2, self.message[2]))
        if self.preamble:
            s_preamble = self.preamble_font.render(self.preamble[0], True, TEXT_COLOR)
            s_box.blit(s_preamble, ((s_box_width - self.preamble[1]) // 2, self.preamble[2]))
        for count_view in self.count_views:
            count_view.draw(s_box)
        theViewer.dealpha(s_box, self.opaque)

        # Scale if needed
        if self.scale > 1.0:
            s_box_width = int(s_box_width * self.scale)
            s_box_height = int(self.box_height * self.scale)
            s_box = pygame.transform.smoothscale(s_box, (s_box_width, s_box_height))

        srf.blit(s_box, ((s_width - s_box_width) // 2, (s_height - s_box_height) // 2))

    def _progress(self, dt):
        # progress all count views
        self.count_t += dt
        if self.count_show:
            for count_view in self.count_views:
                count_view.progress(dt)
        # if interval exceeds, reset counter and make next counter view
        if self.count_t > self.count_interval:
            if self.count > 0:
                self.count_t = self.count_t % self.count_interval
                if self.count_show:
                    count_text = str(self.count) if not self.count_items else self.count_items[-self.count]
                    view = self.Count(self, count_text)
                    self.count_views.append(view)
                    view.show()
                self.count -= 1
            # if count is complete hide the message
            else:
                self.progressive = False
                self.hide()

    class Count(View):
        visible = True
        progressive = True

        t = 0.0

        opaque = 0.0
        shift = None
        color = None

        def __init__(self, _parent, text):
            self._parent = _parent
            self.text = text

        def show(self):
            self.animate(ANI_DIGIT_SHOW)
            self.animate(ANI_DIGIT_COLOR)

        def hide(self):
            self.animate(ANI_DIGIT_HIDE & {'on_end': self._detach_after_hide})
            self.visible = False

        def _detach_after_hide(self):
            self._parent.count_views.remove(self)

        def _progress(self, dt):
            self.t += dt
            if self.t > 1.0:
                self.progressive = False
                self.hide()

        def _draw(self, srf: pygame.SurfaceType):
            width, height = srf.get_size()
            srf_text = self._parent.counter_font.render(self.text, True, self.color)
            theViewer.dealpha(srf_text, self.opaque)
            srf.blit(srf_text, ((width - srf_text.get_width()) // 2 + self.shift, self._parent.counter_y))
