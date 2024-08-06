import numpy, pygame
from engine.viewer import View
from engine.animation import *


class _MenuView(View):
    visible = False

    def __init__(self, spec):
        self._spec = spec
        self.items = list()
        for i, item_spec in enumerate(spec.items):
            self.items.append(self.Item(self, item_spec))
        self.pos = (0,0)
        self.size = (0,0)
        self.reset()

    def update(self):
        pass

    def _reset(self):
        pass

    def _reset_item(self, i, picked):
        pass

    def _show(self):
        pass

    def _hide(self):
        pass

    def _show_item(self, i):
        pass

    def _hide_item(self, i):
        pass

    def _pick(self, i):
        pass

    def _fade(self, i):
        pass

    def _click(self, i):
        pass

    def reset(self):
        self._reset()
        for i, item_view in enumerate(self.items):
            self._reset_item(i, i == self._spec.selected)

    def show(self):
        self.visible = True
        self._show()
        for i, item in enumerate(self.items):
            self._show_item(i)

    def hide(self):
        self.visible = False
        self._hide()
        for i, item in enumerate(self.items):
            self._hide_item(i)
        pass

    def pick(self, i):
        if i is not None and 0 <= i < len(self.items):
            self._pick(i)

    def fade(self, i):
        if i is not None and 0 <= i < len(self.items):
            self._fade(i)

    def click(self, i):
        if i is not None and 0 <= i < len(self.items):
            self._click(i)

    def _is_item_hovered(self, i, pos):
        bounds = self.items[i].get_bounds()
        return None if bounds is None else bounds.move(self.pos).collidepoint(pos)

    def get_hovered_item(self, pos):
        for i, item in enumerate(self.items):
            if self._is_item_hovered(i, pos):
                return i
        return None

    # -------------------- #
    # View for menu items  #
    # -------------------- #
    class Item(View):

        def __init__(self, parent: super, spec):
            self._parent = parent
            self._spec = spec
            self.pos = (0,0)
            self.size = (0,0)

        def get_bounds(self):
            return None if self.size is None or self.pos is None else pygame.Rect(self.pos, self.size)
