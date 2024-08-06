
import math, pygame
import env, views
import engine.shapes as ss

from views.debugger import theDebugger
from engine import theViewer

GA_ACC = 1
GA_RCW = 2
GA_RCCW = 3
GA_FIRE = 4

GH_KEYS_1 = {
    pygame.K_w: GA_ACC,
    pygame.K_a: GA_RCCW,
    pygame.K_d: GA_RCW,
    pygame.K_SPACE: GA_FIRE,
}
GH_KEYS_2 = {
    pygame.K_KP8: GA_ACC,
    pygame.K_KP4: GA_RCCW,
    pygame.K_KP6: GA_RCW,
    pygame.K_KP_ENTER: GA_FIRE,
}
# GH_KEYS_2 = {
#     pygame.K_HOME: GA_ACC,
#     pygame.K_DELETE: GA_RCCW,
#     pygame.K_PAGEDOWN: GA_RCW,
#     pygame.K_KP_ENTER: GA_FIRE,
# }

AREA_WIDTH, AREA_HEIGHT = theViewer.get_screen().get_size()

INI_POS_MARGIN = 35.0

TIME_AFTER_HIT = 1.25


class _Player:
    active = True

    def get_actions(self):
        pass


class HumanPlayer(_Player):
    def __init__(self, **kwargs):
        self.keys = kwargs.pop('keys', None)
        self.name = kwargs.pop('name', None)
        self.score = 0

    def get_actions(self):
        actions = set()
        if self.active:
            keys = pygame.key.get_pressed()
            for key, action in self.keys.items():
                if keys[key]: actions.add(action)
        return actions


class Ship:
    # TODO Rotation acceleration
    # TODO Missile acceleration and adding ship speed
    ANG_INC = 2.75  # increment of angle per second
    ACC_INC = 250.0  # increment of acceleration per second
    ACC_MAX = 150.0  # maximum acceleration
    DEC = 25.0  # deceleration per second

    LENGTH = 45
    THICK = 30
    INNER_THICK = 6

    hit_by = None
    time_after_hit = 0.0

    def __init__(self, pos, ang, player):
        self.player = player
        self.missile = Missile(self)

        self.pos = pos
        self.ang = ang
        self.engines_on = False

        self.spd = [0.0, 0.0]  # speed vector
        self.spd_mod = 0.0  # speed module
        self.spd_ang = 0.0  # speed angle
        self.acc = 0.0  # acceleration module

        self.points = (
            # left wing
            (self.LENGTH / 2, -self.INNER_THICK / 2),
            (-self.LENGTH / 2, -self.INNER_THICK / 2),
            (-self.LENGTH / 2, -self.THICK / 2),
            # right wing
            (self.LENGTH / 2, self.INNER_THICK / 2),
            (-self.LENGTH / 2, self.INNER_THICK / 2),
            (-self.LENGTH / 2, self.THICK / 2),
            # inner
            (self.LENGTH * 3 / 8, self.INNER_THICK / 2),
            (-self.LENGTH * 9 / 20, self.INNER_THICK / 2),
            (-self.LENGTH * 9 / 20, -self.INNER_THICK / 2),
            (self.LENGTH * 3 / 8, -self.INNER_THICK / 2),
            # engine smoke
            (-self.LENGTH * 17 / 30, 0),
            # engine sparks
            (-self.LENGTH * 27 / 50, 0),
        )

    def act(self, dt):

        if self.hit_by is not None:
            self.time_after_hit += dt
        else:

            # Update ship status out of actions
            actions = self.player.get_actions()

            self.engines_on = GA_ACC in actions
            if GA_RCW in actions: self.ang += self.ANG_INC * dt
            if GA_RCCW in actions: self.ang -= self.ANG_INC * dt
            if GA_FIRE in actions: self.missile.fired = True

            self.spd_mod = math.sqrt(self.spd[0] ** 2 + self.spd[1] ** 2)
            self.spd_ang = math.atan2(self.spd[1], self.spd[0])

            # Process ship physics
            if self.engines_on:
                # increase acceleration
                self.acc += self.ACC_INC * dt
                if self.acc > self.ACC_MAX:
                    self.acc = self.ACC_MAX
                # increase speed
                self.spd[0] += self.acc * math.cos(self.ang) * dt
                self.spd[1] += self.acc * math.sin(self.ang) * dt
            else:
                # drop acceleration
                self.acc = 0
                # decrease speed: drop it or decrease with speed angle
                if self.spd_mod < self.DEC * dt:
                    self.spd = [0.0, 0.0]
                else:
                    self.spd[0] -= self.DEC * math.cos(self.spd_ang) * dt
                    self.spd[1] -= self.DEC * math.sin(self.spd_ang) * dt

            # Move ship
            self.pos[0] += self.spd[0] * dt
            self.pos[1] += self.spd[1] * dt
            # process movement on edges
            if self.pos[0] < 0: self.pos[0] = 0; self.spd[0] = 0
            if self.pos[0] > AREA_WIDTH: self.pos[0] = AREA_WIDTH; self.spd[0] = 0
            if self.pos[1] < 0: self.pos[1] = 0; self.spd[1] = 0
            if self.pos[1] > AREA_HEIGHT: self.pos[1] = AREA_HEIGHT; self.spd[1] = 0

        self.missile.act(dt)

        # if DEBUG_SHOW_MSGS: DEBUG_MSGS = [
        #     'ang: {:10.3f}'.format(math.degrees(self.ang)),
        #     'acc: {:10.5f}'.format(self.acc),
        #     'spd_mod: {:10.5f}'.format(self.spd_mod),
        #     'spd_ang: {:10.3f}'.format(math.degrees(self.spd_ang)),
        #     'spdX: {:10.5f}'.format(self.spd[0]),
        #     'spdY: {:10.5f}'.format(self.spd[1]),
        #     'posX: {:6.2f}'.format(self.pos[0]),
        #     'posY: {:6.2f}'.format(self.pos[1]),
        # ]

    def is_hit_by(self, missile):
        # TODO check compound polygon including center
        lines_ship = (
            ss.transform_points((self.points[0], self.points[1]), self.ang, self.pos),
            ss.transform_points((self.points[1], self.points[2]), self.ang, self.pos),
            ss.transform_points((self.points[2], self.points[0]), self.ang, self.pos),
            ss.transform_points((self.points[3], self.points[4]), self.ang, self.pos),
            ss.transform_points((self.points[4], self.points[5]), self.ang, self.pos),
            ss.transform_points((self.points[5], self.points[3]), self.ang, self.pos),
        )
        lines_missile = (
            ss.transform_points((missile.points[0], missile.points[1]), missile.ang, missile.pos),
            ss.transform_points((missile.points[1], missile.points[2]), missile.ang, missile.pos),
            ss.transform_points((missile.points[2], missile.points[3]), missile.ang, missile.pos),
            ss.transform_points((missile.points[3], missile.points[0]), missile.ang, missile.pos),
        )
        return ss.mass_intersects(lines_ship, lines_missile)


class Missile:
    SPD_ = 450.0  # missile speed module
    OFFSCREEN_TH = 20.0  # off-screen threshold
    SEMILENGTH = 9.0
    SEMITHICK = 0.75

    def __init__(self, ship):
        self.ship = ship
        self.pos = [0.0, 0.0]
        self.ang = 0.0
        self.fired = False
        # shape points
        self.points = (
            (self.SEMILENGTH, self.SEMITHICK),
            (-self.SEMILENGTH, self.SEMITHICK),
            (-self.SEMILENGTH, -self.SEMITHICK),
            (self.SEMILENGTH, -self.SEMITHICK),
        )

    def resupply(self):
        """ Place back missile ready to fire """
        self.pos = list(self.ship.pos)
        self.ang = self.ship.ang
        self.fired = False

    def act(self, dt):
        if self.fired:
            self.pos[0] += self.SPD_ * math.cos(self.ang) * dt
            self.pos[1] += self.SPD_ * math.sin(self.ang) * dt
            offscreen_x = self.pos[0] < -self.OFFSCREEN_TH or self.pos[0] > AREA_WIDTH + self.OFFSCREEN_TH
            offscreen_y = self.pos[1] < -self.OFFSCREEN_TH or self.pos[1] > AREA_HEIGHT + self.OFFSCREEN_TH
            if offscreen_x or offscreen_y:
                self.resupply()
        else:
            self.pos = list(self.ship.pos)
            self.ang = self.ship.ang


class Game:
    ships = None
    alive_ships = None
    message_view = None

    time_after_hit = 0.0
    ready = False
    end = False

    def __init__(self, **kwargs):
        self.rounds = kwargs.pop('rounds')
        self.round = 1

        # Players
        self.players = kwargs.pop('players')
        for player in self.players:
            player.score = 0
        self.setup_round()

        # Make viewы
        self.arena = views.Arena(self)
        theViewer.views.insert(2, self.arena)
        self.status = views.arena.Status(self)
        theViewer.attach_after(self.arena, self.status)

    def setup_round(self):
        if self.message_view is not None:
            theViewer.detach(self.message_view)
            self.message_view = None

        self.ships = list()
        # Get layout for players, make ships for them
        layout = self.get_initial_layout()
        for i, player in enumerate(self.players):
            player.active = False
            ship = Ship(layout[i][:2], layout[i][2], player)
            self.ships.append(ship)

        self.alive_ships = self.ships[:]
        self.time_after_hit = 0.0
        self.ready = False
        self.end = False

    def get_initial_layout(self):
        if len(self.players) == 2:
            return (
                [INI_POS_MARGIN, INI_POS_MARGIN, 0.0],
                [AREA_WIDTH - INI_POS_MARGIN, AREA_HEIGHT - INI_POS_MARGIN, math.pi]
            )
        else:
            raise Exception('Only two players allowed yet')

    def get_status_layout(self):
        if len(self.players) == 2:
            return (
                (views.arena.MARGIN, views.arena.MARGIN, views.arena.ALIGN_LFT | views.arena.ALIGN_TOP),
                (AREA_WIDTH - views.arena.MARGIN, AREA_HEIGHT - views.arena.MARGIN, views.arena.ALIGN_RHT | views.arena.ALIGN_BTM)
            )
        else:
            raise Exception('Only two players allowed yet')

    def set_ready(self):
        self.ready = True
        for player in self.players:
            player.active = True
        theViewer.detach(self.message_view)
        self.message_view = None

    def act(self, dt: float):
        """Overall game logic"""

        # Show ready message
        if not self.ready:
            if not self.message_view:
                # Setup message
                preamble = ''
                if self.rounds > 1:
                    if sum(player.score for player in self.players) == 0:
                        preamble = env.GAME_READY_PREAMBLE_FIRST
                    elif any(self.rounds - player.score == 1 for player in self.players):
                        preamble = env.GAME_READY_PREAMBLE_LAST
                    else:
                        preamble = env.GAME_READY_PREAMBLE_NEXT

                self.message_view = views.TransientMessage(
                    message=env.GAME_READY_MESSAGE,
                    preamble=preamble,
                    on_complete=self.set_ready,
                    count=['3', '2', '1', 'GO!'],
                    count_interval=1.0,
                    count_show=True
                )
                theViewer.attach_after(self.arena, self.message_view)
                self.message_view.show()

        # Let ships act
        for ship in self.ships:
            ship.act(dt)

        if not self.end:
            # Process alive ships to be hit by others, alive or not
            for ship in self.alive_ships:
                for other_ship in (x for x in self.ships if x != ship):
                    if other_ship.missile.fired and ship.is_hit_by(other_ship.missile):
                        self.alive_ships.remove(ship)
                        ship.hit_by = other_ship
                        other_ship.missile.resupply()
                        ship.player.active = False

            # Trigger end?
            if len(self.alive_ships) <= 1:
                self.time_after_hit += dt
                if self.time_after_hit > TIME_AFTER_HIT and all(not x.missile.fired for x in self.ships):
                    self.end = True

                    if len(self.alive_ships) == 0:
                        message = env.GAME_DRAW_ROUND_MESSAGE if self.rounds > 1 else env.GAME_DRAW_MESSAGE
                    else:
                        winner = self.alive_ships[0].player
                        winner.active = False
                        message = winner.name + ' '
                        message += env.GAME_WINS_ROUND_MESSAGE if self.rounds > 1 else env.GAME_WINS_MESSAGE
                        winner.score += 1

                    self.message_view = views.TransientMessage(
                        message=message,
                        on_complete=self.setup_round,
                        count=1,
                        count_interval=3.5,
                        count_show=False
                    )
                    theViewer.attach_after(self.arena, self.message_view)
                    self.message_view.show()

        if env.DEBUG_HIT_BY:
            for ship in self.ships:
                if ship.hit_by is not None:
                    theDebugger.messages.append(ship.player.name + ' is hit by ' + ship.hit_by.player.name)



