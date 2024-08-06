
import pygame
from pygame.locals import *
from ext import call, ecall

import env
import game as gg
import views
from engine import theViewer, menu as mm, controls
from views import theDebugger

_MODE_BLANK = 0
_MODE_MENU = 1
_MODE_GAME = 2

_MENU_MAIN = 1
_MENU_LGAME = 2
_MENU_SETTINGS = 3


class App(controls.HandlersHolder):
    _running = True
    _mouse_cursor_visible = False
    mode = _MODE_BLANK

    _current_main_menu = None
    _invoked_menu = None

    game = None # Current game

    players_keys_controls = [
        dict(gg.GH_KEYS_1),
        dict(gg.GH_KEYS_2),
    ]

    t = 0
    dt = 0

    def __init__(self):
        super().__init__()

        # Setting mouse cursor
        pygame.mouse.set_pos(theViewer.get_screen().get_width()//2, theViewer.get_screen().get_height()//2)
        pygame.mouse.set_visible(False)
        pygame.event.clear()

        # Setting app clock
        self.clock = pygame.time.Clock()

        # Setting different menus
        self.quit_menu = mm.HandledMenu(
            title='Sure to exit?',
            items=[
                dict(caption='Yes', run=self.terminate),
                dict(caption='No', run=self.revoke_menu, default=True),
            ],
            view=views.ModalMenuView.ModalMenuView,
            handle=mm.HANDLE_RICH_HORIZONTAL | mm.HANDLE_MOUSE
        )

        self.resume_menu = mm.HandledMenu(
            title='Sure to exit game?',
            items=[
                dict(caption='Exit to main menu', run=self.abort_game),
                dict(caption='Exit to desktop', run=self.terminate),
                dict(caption='Resume game', run=self.revoke_menu, default=True),
            ],
            view=views.ModalMenuView.ModalMenuView,
            handle=mm.HANDLE_RICH_HORIZONTAL | mm.HANDLE_MOUSE
        )

        self.endgame_menu = mm.HandledMenu(
            title='Wins',
            items=[
                dict(caption='Exit to main menu', run=self.abort_game),
                dict(caption='Repeat game', run=None, default=True)
            ],
            view=views.ModalMenuView.ModalMenuView,
            handle=mm.HANDLE_RICH_HORIZONTAL | mm.HANDLE_MOUSE
        )

        self.main_menus = {
            _MENU_MAIN: mm.HandledMenu(
                items=[
                    dict(caption='Local game', run=call(self.change_main_menu, _MENU_LGAME), default=True),
                    dict(caption='Network game', run=None),
                    dict(caption='Settings', run=call(self.change_main_menu, _MENU_SETTINGS)),
                    dict(caption='About', run=None),
                    dict(caption='Exit', run=call(self.invoke_menu, self.quit_menu)),
                ],
                handle=mm.HANDLE_RICH_VERTICAL | mm.HANDLE_MOUSE
        ),
            _MENU_LGAME: mm.HandledMenu(
                title='Local game',
                items=[
                    dict(caption='Back', run=call(self.change_main_menu, _MENU_MAIN), default=True),
                    dict(caption='Rounds', variants=('1', '2', '3', '4', '5', '6', '7'), index=2),
                    dict(caption='Players', variants=('two humans', 'human vs AI'), index=0),
                    dict(caption='Start game', run=self.start_local_game),
                ],
                handle=mm.HANDLE_RICH_VERTICAL | mm.HANDLE_MOUSE | mm.HANDLE_VARIANTS
            ),
            _MENU_SETTINGS: mm.HandledMenu(
                title='Settings',
                items=[
                    dict(caption='Back', run=call(self.change_main_menu, _MENU_MAIN), default=True),
                    dict(caption='Player 1 controls'),
                    dict(caption='Player 2 controls'),
                ],
                handle=mm.HANDLE_RICH_VERTICAL | mm.HANDLE_MOUSE
            ),
        }

        self.handler = controls.Handler({
            pygame.QUIT: [
                (True, ecall(self.terminate))
            ],
            pygame.KEYDOWN: [
                (True, ecall(self.hide_mouse_cursor)),
                (dict(key=pygame.K_ESCAPE), ecall(self.invoke_menu, self.quit_menu))
            ],
            pygame.MOUSEMOTION: [
                (True, ecall(self.show_mouse_cursor))
            ]
        })

        self.attach_handler(self.handler)

        self._vStars = views.Stars()
        theViewer.attach(self._vStars)
        theViewer.attach(theDebugger)

    def tick(self):
        self.dt = self.clock.tick() / 1000

    def show_mouse_cursor(self):
        if not self._mouse_cursor_visible:
            self._mouse_cursor_visible = True
            pygame.mouse.set_visible(True)

    def hide_mouse_cursor(self):
        if self._mouse_cursor_visible:
            self._mouse_cursor_visible = False
            pygame.mouse.set_visible(False)

    def act(self):
        if env.DEBUG_QUICKLY_LOCAL_GAME:
            self.start_local_game()

        while self._running:
            theDebugger.messages = []
            env.DEBUG_POINTS = []
            self.tick()

            #########
            # START #
            #########
            if self.mode == _MODE_BLANK:
                self._vStars.fade_in()
                self.t += self.dt
                if self.t > 0.1:
                    self.t = 0
                    self.change_main_menu(_MENU_MAIN)
                    continue

            ########
            # MENU #
            ########
            elif self.mode == _MODE_MENU:
                for event in pygame.event.get():
                    self.handle(event.type, event.__dict__)

            ########
            # GAME #
            ########
            elif self.mode == _MODE_GAME:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.terminate()
                        break
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        self.invoke_menu(self.resume_menu)
                        continue
                    elif event.type == KEYDOWN and event.key == K_F5:
                        views.arena.DEBUG_HOLLOW_SHIPS = not views.arena.DEBUG_HOLLOW_SHIPS
                        continue
                self.game.act(self.dt)

            if env.DEBUG_FPS:
                theDebugger.messages.append("FPS: " + str(int(self.clock.get_fps())))
            if env.DEBUG_KEYS:
                keys = []
                for i, k in enumerate(pygame.key.get_pressed()):
                    if k:
                        keys.append(pygame.key.name(i))
                theDebugger.messages.append("Keys: " + str(keys))

            theViewer.progress(self.dt)
            theViewer.draw()

    def terminate(self):
        self._running = False

    def invoke_menu(self, menu: mm.Menu):
        self._invoked_menu = menu
        self.attach_handler(menu.handler)
        for handler in self.all_handlers_before(menu.handler):
            handler.active = False
        theViewer.attach_before(theDebugger, menu.view)
        menu.select_default()
        menu.view.reset()
        menu.view.show()

    def revoke_menu(self):
        for handler in self.all_handlers_before(self._invoked_menu.handler):
            handler.active = True
        self.detach_handler(self._invoked_menu.handler)
        self._invoked_menu.view.hide()
        self._invoked_menu = None

    def change_main_menu(self, main_menu_id, i=0):
        self.mode = _MODE_MENU
        if self._current_main_menu is not None:
            self._current_main_menu.view.hide()
            self.detach_handler(self._current_main_menu.handler)

        self._current_main_menu = self.main_menus[main_menu_id]
        self.attach_handler(self._current_main_menu.handler)

        theViewer.attach_before(theDebugger, self._current_main_menu.view)
        self._current_main_menu.view.reset()
        self._current_main_menu.view.show()

    def start_local_game(self):
        # if self.main_menu is not None:
        #     self.main_menu.view.hide()
        if self._current_main_menu is not None:
            self._current_main_menu.view.hide()

        self.game = gg.Game(
            players=[
                gg.HumanPlayer(
                    name='Player 1',
                    keys=self.players_keys_controls[0]
                ),
                gg.HumanPlayer(
                    name='Player 2',
                    keys=self.players_keys_controls[1]
                ),
            ],
            rounds=15
        )

        # self.game.ready_view = self.ready_view

        self.mode = _MODE_GAME
        # theViewer.views[2].set_game(self.game)
        # theViewer.views[2].visible = True
        # theViewer.views[2].progressive = True

    def abort_game(self):
        self.revoke_menu()
        theViewer.views[2].visible = False
        theViewer.views[2].progressive = False
        theViewer.views[2].set_game(None)
        self.game = None
        # self.show_menu(self.MENU_MAIN)
        self.mode = _MODE_BLANK


# class AppHandler(controls.Handler):
#
#     def __init__(self):
#         self.handling = {
#             pygame.KEYDOWN: {
#                 dict(key=pygame.K_ESCAPE): app.terminate
#             },
#             pygame.QUIT: app.terminate
#         }
#         pass
