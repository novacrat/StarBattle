
import pygame
from engine.animation import Animation, Transition
from views.debugger import theDebugger
from engine import theViewer
from views.MenuView import _MenuView
from ext import call, ecall


SHUTTER_COLOR = 30, 0, 10
SHUTTER_ALPHA = 100

BLOCK_COLOR = 20, 0, 50, 220

TITLE_TOP_MARGIN = 30
TITLE_COLOR = 255, 255, 255

ITEMS_TOP_MARGIN = 100
ITEMS_GAP = 10
ITEM_SHOW_DELAY = .25
ITEM_HIDE_DELAY = .2
ITEM_HIDE_SHIFT = -75

ITEM_BOX_EXPAND_X = 30
ITEM_BOX_EXPAND_Y = 10
ITEM_BOX_PADDING_X = 15
ITEM_BOX_PADDING_Y = 7

ITEM_TEXT_COLOR = 150, 160, 235
ITEM_TEXT_PICK_COLOR = 255, 255, 255
ITEM_BOX_COLOR = 30, 10, 70, 50
ITEM_BOX_PICK_COLOR = 25, 75, 155, 150
ITEM_BOX_CLICK_COLOR = 255, 230, 255, 150


ANI_CLICK = Animation(
    text_color=ITEM_TEXT_PICK_COLOR, ___box_color=ITEM_BOX_CLICK_COLOR, box_color=ITEM_BOX_PICK_COLOR,
    duration=.5,
)
ANI_PICK = Animation(
    text_color=ITEM_TEXT_PICK_COLOR, box_color=ITEM_BOX_PICK_COLOR,
    duration=.15
)
ANI_FADE = Animation(
    text_color=ITEM_TEXT_COLOR, box_color=ITEM_BOX_COLOR,
    duration=.55
)
ANI_SHOW = Animation(
    opaque=1.0,
    duration=.35, transition=Transition.easeOutSine
)
ANI_HIDE = Animation(
    opaque=0.0,
    duration=.15, transition=Transition.easeOutSine
)


class ModalMenuView(_MenuView):
    opaque = None
    shutter_alpha = None

    def __init__(self, spec):
        self.title_font = pygame.font.Font('fonts/Orbitron Light.otf', 42)
        self.font = pygame.font.Font('fonts/Orbitron Bold.otf', 24)
        self.items_total_width = 0
        super().__init__(spec)

    def _reset(self):
        width, height = theViewer.get_screen().get_size()
        self.pos = (0, height*1.5//4)
        self.size = (width, height//4)
        if self.visible:
            self.opaque = 1.0
            self.shutter_alpha = SHUTTER_ALPHA
        else:
            self.opaque = 0.0
            self.shutter_alpha = 0

    def _reset_item(self, i, picked):
        item = self.items[i]
        if self.visible:
            item.pos = self._centered_item_pos((item.margin, ITEMS_TOP_MARGIN))
            item.opaque = 1.0
        else:
            item.pos = self._centered_item_pos((item.margin + ITEM_HIDE_SHIFT, ITEMS_TOP_MARGIN))
            item.opaque = 0.0
        if picked:
            item.text_color = ITEM_TEXT_PICK_COLOR
            item.box_color = ITEM_BOX_PICK_COLOR
        else:
            item.text_color = ITEM_TEXT_COLOR
            item.box_color = ITEM_BOX_COLOR

    def _centered_item_pos(self, pos):
        return pos[0] + (self.size[0]-self.items_total_width)//2, pos[1]

    def _centered_pos_x(self, width, pos_x=0):
        return (self.size[0] - width)//2 + pos_x

    def _show(self):
        self.animate(ANI_SHOW & {'shutter_alpha': SHUTTER_ALPHA})

    def _hide(self):
        self.animate(ANI_HIDE & {'shutter_alpha': 0, 'on_end': call(theViewer.detach, self)})

    def _show_item(self, i):
        self.items[i].animate(ANI_SHOW & {
            'delay': i * ITEM_SHOW_DELAY,
            'pos': self._centered_item_pos((self.items[i].margin, ITEMS_TOP_MARGIN))
        })

    def _hide_item(self, i):
        self.items[i].animate(ANI_HIDE & {
            'delay': i * ITEM_HIDE_DELAY,
            'pos': self._centered_item_pos((self.items[i].margin + ITEM_HIDE_SHIFT, ITEMS_TOP_MARGIN))
        })

    def _pick(self, i):
        self.items[i].animate(ANI_PICK)

    def _fade(self, i):
        self.items[i].animate(ANI_FADE)

    def _click(self, i):
        self.items[i].animate(ANI_CLICK)

    def _draw(self, srf: pygame.SurfaceType):
        # Shutter, adjusted with alpha
        pygame.gfxdraw.box(srf, srf.get_rect(), list(SHUTTER_COLOR)+[self.shutter_alpha])
        # theViewer.darken(srf, 0.0)

        # Modal Box with Title
        srf_menu = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        srf_menu.fill(BLOCK_COLOR)
        if self._spec.title:
            srf_title = self.title_font.render(self._spec.title, True, TITLE_COLOR)
            srf_menu.blit(srf_title, (self._centered_pos_x(srf_title.get_width()), TITLE_TOP_MARGIN))

        # Items
        for item in self.items:
            item.draw(srf_menu)

        # Overall opaque and blit
        theViewer.dealpha(srf_menu, self.opaque)
        srf.blit(srf_menu, self.pos)

    # -------------------- #
    # View for menu items  #
    # -------------------- #
    class Item(_MenuView.Item):
        opaque = None
        text_color = None
        box_color = None

        def __init__(self, parent: super, spec):
            super().__init__(parent, spec)
            size_x, size_y = self._parent.font.size(self._spec['caption'])
            size_x += ITEM_BOX_EXPAND_X
            size_y += ITEM_BOX_EXPAND_Y
            self.size = (size_x, size_y)
            self.margin = self._parent.items_total_width
            self._parent.items_total_width += size_x + ITEMS_GAP

        def _draw(self, srf):
            # Box, adjusted with opaque
            srf_box = pygame.Surface(self.size, pygame.SRCALPHA, 32)
            srf_box.fill(list(self.box_color[0:3]) + [int(self.box_color[3]*self.opaque)])

            # Text over box, adjusted with opaque
            srf_text = self._parent.font.render(self._spec['caption'], True, self.text_color)
            theViewer.dealpha(srf_text, self.opaque)
            srf_box.blit(srf_text, (ITEM_BOX_PADDING_X, ITEM_BOX_PADDING_Y))

            srf.blit(srf_box, self.pos)

