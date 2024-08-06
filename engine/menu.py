
import pygame
import views
from . import controls
from ext import call


A_NEXT = 1
A_PREV = 2
A_INC = 3
A_DEC = 4
A_RUN = 5
A_HOVER = 6

HANDLE_VERTICAL = 0x0001
HANDLE_HORIZONTAL = 0x0002
HANDLE_KP_ENTER = 0x0010
HANDLE_SPACE = 0x0020
HANDLE_BACKSPACE = 0x0040
HANDLE_VARIANTS = 0x0100
HANDLE_MOUSE = 0x1000
# compound handles
HANDLE_RICH_VERTICAL = 0x00f1
HANDLE_RICH_HORIZONTAL = 0x00f2
HANDLE_ALL_VERTICAL = 0x11f1


class Menu():

    def __init__(self, **kwargs):
        self.title = kwargs.pop('title', '')
        self.items = kwargs.pop('items', [])[:]
        self.cyclic = kwargs.pop('cyclic', True)

        # setting default and select it
        self.default = None
        for i, item in enumerate(self.items):
            if 'default' in item and item['default'] is True:
                self.default = i
        self.selected = self.default

        #view
        self.view = kwargs.pop('view', views.CommonMenuView.CommonMenuView)(self)

    def select_next(self):
        if self.selected is None:
            self.selected = 0
        else:
            self.selected += 1
            if self.selected > len(self.items)-1:
                self.selected = 0 if self.cyclic else len(self.items)-1

    def select_prev(self):
        if self.selected is None:
            self.selected = len(self.items)-1
        else:
            self.selected -= 1
            if self.selected < 0:
                self.selected = len(self.items)-1 if self.cyclic else 0

    def select(self, i):
        self.selected = i if i is not None and (0 <= i < len(self.items)) else None

    def select_default(self, or_i=None):
        if self.default is not None:
            self.selected = self.default
        else:
            self.selected = or_i if or_i is not None and (0 <= or_i < len(self.items)) else None

    def inc_variant(self):
        if self.selected is not None and 'variants' in self.items[self.selected]:
            item = self.items[self.selected]
            item['index'] += 1
            if item['index'] > len(item['variants'])-1:
                item['index'] = len(item['variants'])-1
        self.view.update()

    def dec_variant(self):
        if self.selected is not None and 'variants' in self.items[self.selected]:
            item = self.items[self.selected]
            item['index'] -= 1
            if item['index'] < 0:
                item['index'] = 0
        self.view.update()

    # ACTIONS
    def act(self, action, **kwargs):
        if action == A_NEXT:
            self.view.fade(self.selected)
            self.select_next()
            self.view.pick(self.selected)

        elif action == A_PREV:
            self.view.fade(self.selected)
            self.select_prev()
            self.view.pick(self.selected)

        elif action == A_HOVER:
            i = self.view.get_hovered_item(kwargs['pos'])
            if i is not None and i != self.selected:
                self.view.fade(self.selected)
                self.select(i)
                self.view.pick(self.selected)

        elif self.selected is not None:
            if action == A_RUN:
                if 'run' in self.items[self.selected]:
                    self.view.click(self.selected)
                    self.items[self.selected]['run']()
                else:
                    self.act(A_INC)
            else:
                if 'variants' in self.items[self.selected]:
                    if action == A_INC:
                        self.inc_variant()
                        self.view.click(self.selected)
                    elif action == A_DEC:
                        self.dec_variant()
                        self.view.click(self.selected)


class HandledMenu(Menu):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        handle_settings = kwargs.pop('handle', HANDLE_ALL_VERTICAL)
        handling = dict()

        # keys handling
        if handle_settings & (HANDLE_VERTICAL | HANDLE_HORIZONTAL):
            handling_keys = [
                (dict(key=pygame.K_RETURN), call(self.act, A_RUN)),
            ]
            handling_keys += [
                (dict(key=pygame.K_DOWN), call(self.act, A_NEXT)),
                (dict(key=pygame.K_UP), call(self.act, A_PREV)),
            ] if handle_settings & HANDLE_VERTICAL else [
                (dict(key=pygame.K_RIGHT), call(self.act, A_NEXT)),
                (dict(key=pygame.K_LEFT), call(self.act, A_PREV)),
            ]
            if handle_settings & HANDLE_VARIANTS:
                handling_keys += [
                    (dict(key=pygame.K_LEFT), call(self.act, A_DEC)),
                    (dict(key=pygame.K_RIGHT), call(self.act, A_INC)),
                ] if handle_settings & HANDLE_VERTICAL else [
                    (dict(key=pygame.K_DOWN), call(self.act, A_DEC)),
                    (dict(key=pygame.K_UP), call(self.act, A_INC)),
                ]
                if handle_settings & HANDLE_BACKSPACE:
                    handling_keys += [
                        (dict(key=pygame.K_BACKSPACE), call(self.act, A_DEC)),
                    ]
            if handle_settings & HANDLE_KP_ENTER:
                handling_keys += [
                    (dict(key=pygame.K_KP_ENTER), call(self.act, A_RUN)),
                ]
            handling[pygame.KEYDOWN] = handling_keys

        #mouse handling
        if handle_settings & HANDLE_MOUSE:
            handling[pygame.MOUSEMOTION] = [
                tuple((dict(), call(self.act, A_HOVER)))
            ]
            handling[pygame.MOUSEBUTTONUP] = [
                (dict(button=1), call(self.act, A_HOVER), call(self.act, A_RUN)),
            ]
            if handle_settings & HANDLE_VARIANTS:
                handling[pygame.MOUSEBUTTONUP] += [
                    (dict(button=3), call(self.act, A_HOVER), call(self.act, A_DEC)),
                    (dict(button=4), call(self.act, A_HOVER), call(self.act, A_INC)),
                    (dict(button=5), call(self.act, A_HOVER), call(self.act, A_DEC)),
                ]

        self.handler = controls.Handler(handling)
