
import pygame
from engine.animation import Animation, Transition
from views.debugger import theDebugger
from engine import theViewer
from views.MenuView import _MenuView
from ext import call, ecall


#todo: menu title participate in surfeace width calculation

MENU_POS = (100,300)
MENU_POS_HIDDEN = (-100,300)

ITEMS_TOP_MARGIN = 65
ITEMS_SPACING = 45
ITEMS_SHOW_SHIFT = 50
ITEMS_HIDE_SHIFT = 0
ITEM_SHOW_DELAY = .25
ITEM_HIDE_DELAY = .2

ITEM_BOX_EXPAND_X = 30
ITEM_BOX_EXPAND_Y = 10
ITEM_BOX_PADDING_X = 15
ITEM_BOX_PADDING_Y = 7

ITEM_TEXT_COLOR = 150, 160, 235
ITEM_TEXT_PICK_COLOR = 255, 255, 255
ITEM_VARIANT_COLOR = 250, 200, 135
ITEM_VARIANT_PICK_COLOR = 255, 235, 200
ITEM_BOX_COLOR = 20, 30, 50, 0
ITEM_BOX_PICK_COLOR = 25, 75, 155, 120
ITEM_BOX_CLICK_COLOR = 255, 230, 255, 120


ANI_CLICK = Animation(
    text_color=ITEM_TEXT_PICK_COLOR, variant_color=ITEM_VARIANT_PICK_COLOR,
    ___box_color=ITEM_BOX_CLICK_COLOR, box_color=ITEM_BOX_PICK_COLOR,
    duration=.5,
)
ANI_PICK = Animation(
    text_color=ITEM_TEXT_PICK_COLOR, variant_color=ITEM_VARIANT_PICK_COLOR,
    box_color=ITEM_BOX_PICK_COLOR,
    duration=.15
)
ANI_FADE = Animation(
    text_color=ITEM_TEXT_COLOR, variant_color=ITEM_VARIANT_COLOR,
    box_color=ITEM_BOX_COLOR,
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


class CommonMenuView(_MenuView):
    opaque = None

    def __init__(self, spec):
        self.title_font = pygame.font.Font('fonts/Orbitron Light.otf', 38)
        self.font = pygame.font.Font('fonts/Orbitron Bold.otf', 26)
        super().__init__(spec)
        self.update()

    def _reset(self):
        if self.visible:
            self.opaque = 1.0
            self.pos = MENU_POS
        else:
            self.opaque = 0.0
            self.pos = MENU_POS_HIDDEN

    def _reset_item(self, i, picked):
        item = self.items[i]
        if self.visible:
            item.pos = (ITEMS_SHOW_SHIFT, ITEMS_SPACING*i + ITEMS_TOP_MARGIN)
            item.opaque = 1.0
        else:
            item.pos = (ITEMS_HIDE_SHIFT, ITEMS_SPACING*i + ITEMS_TOP_MARGIN)
            item.opaque = 0.0
        if picked:
            item.text_color = ITEM_TEXT_PICK_COLOR
            item.variant_color = ITEM_VARIANT_PICK_COLOR
            item.box_color = ITEM_BOX_PICK_COLOR
        else:
            item.text_color = ITEM_TEXT_COLOR
            item.variant_color = ITEM_VARIANT_COLOR
            item.box_color = ITEM_BOX_COLOR

    def update(self):
        items_widths = list()
        for item in self.items:
            item.update()
            items_widths.append(item.size[0])
        self.size = (max(items_widths) + ITEMS_SHOW_SHIFT, ITEMS_SPACING * len(self.items) + ITEMS_TOP_MARGIN)

    def _show(self):
        self.animate(ANI_SHOW & {'pos': MENU_POS})

    def _hide(self):
        self.animate(ANI_HIDE & {'pos': MENU_POS_HIDDEN, 'on_end': call(theViewer.detach, self)})

    def _show_item(self, i):
        self.items[i].animate(ANI_SHOW & {
            'delay': i * ITEM_SHOW_DELAY,
            'pos': (ITEMS_SHOW_SHIFT, self.items[i].pos[1])
        })

    def _hide_item(self, i):
        self.items[i].animate(ANI_HIDE & {
            'delay': i * ITEM_HIDE_DELAY,
            'pos': (ITEMS_HIDE_SHIFT, self.items[i].pos[1])
        })

    def _pick(self, i):
        self.items[i].animate(ANI_PICK)

    def _fade(self, i):
        self.items[i].animate(ANI_FADE)

    def _click(self, i):
        self.items[i].animate(ANI_CLICK)

    def _draw(self, srf):
        srf_menu = pygame.Surface(self.size, pygame.SRCALPHA, 32)

        # Title
        if self._spec.title:
            text = self.title_font.render(self._spec.title, True, (255,255,255))
            srf_menu.blit(text, (ITEMS_SHOW_SHIFT + ITEM_BOX_PADDING_X, 0))

        # Items
        for item in self.items:
            item.draw(srf_menu)

        theViewer.dealpha(srf_menu, self.opaque)
        srf.blit(srf_menu, self.pos)

    # --------------------#
    # View for menu items #
    # --------------------#
    class Item(_MenuView.Item):
        opaque = None
        text_color = None
        variant_color = None
        box_color = None

        def __init__(self, parent: super, spec):
            super().__init__(parent, spec)
            # self.update()

        def update(self):
            caption = self._spec['caption']
            if 'variants' in self._spec:
                caption += ': ' + self._spec['variants'][self._spec['index']]
            size_x, size_y = self._parent.font.size(caption)
            size_x += ITEM_BOX_EXPAND_X
            size_y += ITEM_BOX_EXPAND_Y
            self.size = (size_x, size_y)

        def _draw(self, srf):
            # Box, adjusted with opaque
            srf_box = pygame.Surface(self.size, pygame.SRCALPHA, 32)
            srf_box.fill(list(self.box_color[0:3]) + [int(self.box_color[3]*self.opaque)])

            variant_caption = self._spec['variants'][self._spec['index']] if 'variants' in self._spec else None
            caption = self._spec['caption'] if variant_caption is None else self._spec['caption'] + ': '

            # Text over box, adjusted with opaque
            srf_caption = self._parent.font.render(caption, True, self.text_color)
            theViewer.dealpha(srf_caption, self.opaque)
            srf_box.blit(srf_caption, (ITEM_BOX_PADDING_X, ITEM_BOX_PADDING_Y))

            # Variant text over box, adjusted with opaque
            if variant_caption is not None:
                srf_variant = self._parent.font.render(variant_caption, True, self.variant_color)
                theViewer.dealpha(srf_variant, self.opaque)
                srf_box.blit(srf_variant, (ITEM_BOX_PADDING_X + srf_caption.get_width(), ITEM_BOX_PADDING_Y))

            srf.blit(srf_box, self.pos)
