
import random, math, pygame, pygame.gfxdraw
from engine.animation import Animation, Transition
from views.debugger import theDebugger
from engine import View, theViewer, Gradient, Particles
import game as gg, env, engine.shapes as ss


MISSILE_COLOR = 205, 205, 0
SHIP_COLOR_WING = 120, 120, 120
SHIP_COLOR_WING_EDGE = 175, 175, 185
SHIP_COLOR_INNER = 90, 90, 100

SMOKE_DOT_POINTS = 5
SMOKE_COLORS = Gradient({
    0.0: (200, 230, 255, 75),
    0.05: (180, 220, 255, 25),
    0.11: (100, 100, 100, 10),
    0.55: (90, 90, 90, 5),
    1.0: (250, 250, 250, 0)
})
SMOKE_SIZES = Gradient({
    0.0: 2.0,
    0.05: 5.0,
    0.15: 20.0,
    0.5: 30.0,
    1.0: 39.0
})

IDLE_COLORS = Gradient({
    0.0: (180, 220, 255, 2),
    0.2: (120, 120, 120, 15),
    1.0: (250, 250, 250, 0)
})
IDLE_SIZES = Gradient({
    0.0: 2.0,
    0.1: 5.0,
    1.0: 7.0
})

SPARK_COLORS = Gradient({
    0.0: (255, 225, 255, 255),
    0.35: (115, 220, 255, 255),
    0.75: (100, 120, 255, 100),
    1.0: (100, 110, 150, 0)
})
SPARK_SIZES = Gradient({
    0.0: 0.5,
    0.3: 2.0,
    1.0: 0.5
})

EXPLOSION_DURATION = 0.5
EXPLOSION_COLORS = Gradient({
    0.0: (255, 225, 255, 170),
    0.25: (255, 220, 150, 30),
    0.35: (255, 20, 0, 10),
    0.95: (155, 30, 0, 10),
    1.0: (50, 50, 0, 0)
})
EXPLOSION_SIZES = Gradient({
    0.0: 5.5,
    0.1: 20.0,
    0.3: 7.0,
    0.7: 5.0,
    1.0: 3.0
})

MARGIN = 10

ALIGN_LFT = 0x01
ALIGN_RHT = 0x02
ALIGN_CTR = 0x04
ALIGN_TOP = 0x10
ALIGN_BTM = 0x20


class SmokeParticles(Particles):
    class Particle(Particles.Particle):
        DEC = 155.0     # speed decrease per second
        SPD_ = 25.0      # speed module
        SHIP_SPD_FACTOR = 0.75
        ANG_JITTER = 0.35
        LIFESPAN_MIN = 2.75
        LIFESPAN_MAX = 5.50

        def __init__(self, **kwargs):
            self.lifespan = random.uniform(self.LIFESPAN_MIN, self.LIFESPAN_MAX)
            self.pos = list(kwargs['pos'])
            self.ang = kwargs['ang'] + math.pi + random.uniform(-self.ANG_JITTER, self.ANG_JITTER)
            self.ang_cos = math.cos(self.ang)
            self.ang_sin = math.sin(self.ang)
            self.spd_ = self.SPD_ + kwargs['ship_spd_'] * self.SHIP_SPD_FACTOR

        def progress(self, dt):
            super().progress(dt)
            spd_dec = self.DEC * dt
            if self.spd_ > spd_dec:
                self.spd_ -= spd_dec
                self.pos[0] += self.spd_ * self.ang_cos * dt
                self.pos[1] += self.spd_ * self.ang_sin * dt


class IdleParticles(SmokeParticles):
    class Particle(SmokeParticles.Particle):
        DEC = 7.7
        SPD_ = 11.0
        SHIP_SPD_FACTOR = 0.02
        ANG_JITTER = .75
        LIFESPAN_MIN = 0.0
        LIFESPAN_MAX = 3.5


class SparksParticles(IdleParticles):
    class Particle(IdleParticles.Particle):
        DEC = 75.0
        SPD_ = 100.0
        SHIP_SPD_FACTOR = 0.05
        ANG_JITTER = .05
        LIFESPAN_MIN = 0.02
        LIFESPAN_MAX = 0.10
        REAR_SPREAD = 3.5
        ANG_SPREAD_FACTOR = 0.04

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # adjust spark position along rear part
            athwart_ang = self.ang+math.pi/2
            rear_spread = random.uniform(-self.REAR_SPREAD, self.REAR_SPREAD)
            self.pos[0] += math.cos(athwart_ang) * rear_spread
            self.pos[1] += math.sin(athwart_ang) * rear_spread
            # adjust angle to face in center
            self.ang -= math.pi * self.ANG_SPREAD_FACTOR * (rear_spread / self.REAR_SPREAD)
            self.ang_cos = math.cos(self.ang)
            self.ang_sin = math.sin(self.ang)


class ExplosionParticles(Particles):
    class Particle(Particles.Particle):
        DEC = 100.0
        ANG_JITTER = 0.25
        POS_JITTER = 20.0
        SPD_JITTER_MIN = 85.0
        SPD_JITTER_MAX = 175.0

        def __init__(self, **kwargs):
            lifespan = kwargs.pop('lifespan', 1.0)
            self.lifespan = random.uniform(0.25 * lifespan, 1.75 * lifespan)
            self.pos = list(kwargs.pop('pos'))
            self.ang = kwargs.pop('ang') % (2 * math.pi)
            self.spd = kwargs.pop('ship_spd_mod') / 1.5

            self.pos[0] += random.randint(0, self.POS_JITTER)
            self.pos[1] += random.randint(0, self.POS_JITTER)

            j_ang = random.uniform(0.0, 2 * math.pi)
            j_spd = random.uniform(self.SPD_JITTER_MIN, self.SPD_JITTER_MAX)

            self.size = random.uniform(0.1, 1.5)
            self.ang = j_ang
            self.spd = j_spd / math.sqrt(self.size)

            spd = (self.spd * math.cos(self.ang), self.spd * math.sin(self.ang))
            ship_spd = list(kwargs.pop('ship_spd'))
            # print(ship_spd)
            ship_spd[0] += spd[0]
            ship_spd[1] += spd[1]

            self.spd = math.sqrt(ship_spd[0]**2 + ship_spd[1]**2)
            self.ang = math.atan2(ship_spd[1], ship_spd[0])

        def progress(self, dt):
            super().progress(dt)
            spd_dec = self.DEC * dt
            if self.spd > spd_dec:
                self.spd -= spd_dec
                self.pos[0] += self.spd * math.cos(self.ang) * dt
                self.pos[1] += self.spd * math.sin(self.ang) * dt


class Arena(View):
    visible = True
    progressive = True
    game = None

    def __init__(self, game):
        self.gas_points = ss.circle_points(1.0, SMOKE_DOT_POINTS)
        self.smoke = SmokeParticles(rate=50)
        self.idle_smoke = IdleParticles(rate=10)
        self.sparks = SparksParticles(rate=None, at_once=10)
        self.missiles_smoke = IdleParticles(rate=50, lifespan=0.5, at_once=2)
        self.explosion = ExplosionParticles(rate=100, at_once=15)
        self.game = game

    def _progress(self, dt):
        for ship in self.game.ships:
            if ship.hit_by is not None:
                if ship.time_after_hit < EXPLOSION_DURATION:
                    self.explosion.produce(
                        dt,
                        pos=ship.pos,
                        ang=ship.ang,
                        ship_spd_mod=ship.spd_mod,
                        ship_spd=ship.spd
                    )
            else:
                if ship.engines_on:
                    self.smoke.produce(
                        dt,
                        pos=ss.transform_point(ship.points[10], ship.ang, ship.pos),
                        ang=ship.ang,
                        ship_spd_=ship.spd_mod
                    )
                    self.sparks.produce(
                        dt,
                        pos=ss.transform_point(ship.points[11], ship.ang, ship.pos),
                        ang=ship.ang,
                        ship_spd_=ship.spd_mod
                    )
                else:
                    self.idle_smoke.produce(
                        dt,
                        pos=ss.transform_point(ship.points[10], ship.ang, ship.pos),
                        ang=ship.ang,
                        ship_spd_=ship.spd_mod
                    )

            if ship.missile.fired:
                self.missiles_smoke.produce(
                    dt,
                    # pos=gg.Game.adjust_point(ship.missile.pos, ship.missile.ang, ship.pos),
                    pos=ship.missile.pos,
                    ang=ship.missile.ang,
                    ship_spd_=ship.missile.SPD_
                )

        self.smoke.progress(dt)
        self.sparks.progress(dt)
        self.idle_smoke.progress(dt)
        self.missiles_smoke.progress(dt)
        self.explosion.progress(dt)

    def _draw(self, srf: pygame.SurfaceType):
        srf.lock()

        for ship in self.game.ships:
            if ship.hit_by is None:
                self.draw_ship(srf, ship)
                self.draw_missile(srf, ship.missile)
            else:
                if ship.missile.fired:
                    self.draw_missile(srf, ship.missile)

        for p in self.smoke.particles[::1]:
            color = SMOKE_COLORS.fetch_value(p.t)
            size = SMOKE_SIZES.fetch_value(p.t)
            points = ss.transform_points(self.gas_points, random.random(), p.pos, size)
            pygame.gfxdraw.filled_polygon(srf, points, color)

        for p in self.idle_smoke.particles[::1]:
            color = IDLE_COLORS.fetch_value(p.t)
            size = IDLE_SIZES.fetch_value(p.t)
            points = ss.transform_points(self.gas_points, random.random(), p.pos, size)
            pygame.gfxdraw.filled_polygon(srf, points, color)

        for p in self.missiles_smoke.particles[::1]:
            color = IDLE_COLORS.fetch_value(p.t)
            size = IDLE_SIZES.fetch_value(p.t)
            points = ss.transform_points(self.gas_points, random.random(), p.pos, size * 1.7)
            pygame.gfxdraw.filled_polygon(srf, points, color)

        for p in self.sparks.particles[::1]:
            color = SPARK_COLORS.fetch_value(p.t)
            size = SPARK_SIZES.fetch_value(p.t)
            endpos = (
                p.pos[0] + p.spd_ * math.cos(p.ang) * .025,
                p.pos[1] + p.spd_ * math.sin(p.ang) * .025,
            )
            pygame.draw.aaline(srf, color, p.pos, endpos)
            points = ss.transform_points(self.gas_points, random.random(), p.pos, size)
            pygame.gfxdraw.filled_polygon(srf, points, color)

        for p in self.explosion.particles[::1]:
            color = EXPLOSION_COLORS.fetch_value(p.t)
            size = EXPLOSION_SIZES.fetch_value(p.t)
            points = ss.transform_points(self.gas_points, random.random(), p.pos, size * p.size)
            pygame.gfxdraw.filled_polygon(srf, points, color)

        srf.unlock()

        if env.DEBUG_SHOW_POINTS:
            theDebugger.messages.append('DEBUG POINTS: ' + str(len(env.DEBUG_POINTS)))
            for p in env.DEBUG_POINTS:
                points = ss.transform_points(self.gas_points, 0.0, p, 3.0)
                pygame.gfxdraw.filled_polygon(srf, points, (255,0,128,200))
                # pygame.draw.aaline(srf, (255,0,0), p, p)

        theDebugger.messages.append('Smoke particles: ' + str(len(self.smoke.particles)))
        theDebugger.messages.append('Sparks particles: ' + str(len(self.sparks.particles)))
        theDebugger.messages.append('Idle smoke particles: ' + str(len(self.idle_smoke.particles)))
        theDebugger.messages.append('Missile smoke particles: ' + str(len(self.missiles_smoke.particles)))
        if env.DEBUG_HOLLOW_SHIPS:
            theDebugger.messages.append("Ships hollowed")

    @staticmethod
    def draw_missile(srf: pygame.SurfaceType, missile):
        points = ss.transform_points(missile.points, missile.ang, missile.pos)
        if not env.DEBUG_HOLLOW_SHIPS:
            pygame.gfxdraw.aapolygon(srf, points, MISSILE_COLOR)
            pygame.gfxdraw.filled_polygon(srf, points, MISSILE_COLOR)
        pygame.draw.aalines(srf, MISSILE_COLOR, True, points)

    @staticmethod
    def draw_ship(srf: pygame.SurfaceType, ship):
        left_wing = ss.transform_points(ship.points[0:3], ship.ang, ship.pos)
        right_wing = ss.transform_points(ship.points[3:6], ship.ang, ship.pos)
        inner = ss.transform_points(ship.points[6:10], ship.ang, ship.pos)
        if not env.DEBUG_HOLLOW_SHIPS:
            pygame.gfxdraw.aapolygon(srf, inner, SHIP_COLOR_INNER)
            pygame.gfxdraw.filled_polygon(srf, inner, SHIP_COLOR_INNER)
            pygame.gfxdraw.aapolygon(srf, left_wing, SHIP_COLOR_WING)
            pygame.gfxdraw.aapolygon(srf, right_wing, SHIP_COLOR_WING)
            pygame.gfxdraw.filled_polygon(srf, left_wing, SHIP_COLOR_WING)
            pygame.gfxdraw.filled_polygon(srf, right_wing, SHIP_COLOR_WING)
        pygame.draw.aalines(srf, SHIP_COLOR_INNER, True, inner)
        pygame.draw.aalines(srf, SHIP_COLOR_WING_EDGE, True, left_wing)
        pygame.draw.aalines(srf, SHIP_COLOR_WING_EDGE, True, right_wing)

        if env.DEBUG_SHOW_SPEED_VECTOR:
            pygame.draw.aaline(srf, (255, 255, 0), ship.pos, ss.transform_point((100,0), ship.spd_ang, ship.pos))


class Status(View):
    visible = True
    progressive = True
    game = None

    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font('fonts/Orbitron Medium.otf', 12)
        self.score_font = pygame.font.Font('fonts/Orbitron Black.otf', 12)
        self.layout = game.get_status_layout()

    @staticmethod
    def get_text_pos(size, pos, align, shift=0):
        if align & ALIGN_LFT:
            pos_x = pos[0] + shift
        elif align & ALIGN_RHT:
            pos_x = pos[0] - size[0] - shift
        else:
            pos_x = (pos[0] - size[0] - shift) // 2
        if align & ALIGN_TOP:
            pos_y = pos[1]
        else:
            pos_y = pos[1] - size[1]
        return pos_x, pos_y

    def _draw(self, srf: pygame.SurfaceType):
        for i, player in enumerate(self.game.players):

            name = self.font.render(player.name, True, (255, 255, 255))
            theViewer.dealpha(name, 0.5)
            srf.blit(name, self.get_text_pos(name.get_size(), self.layout[i][:2], self.layout[i][2]))

            score = self.score_font.render(str(player.score), True, (210, 235, 255))
            theViewer.dealpha(score, 0.75)
            srf.blit(score, self.get_text_pos(score.get_size(), self.layout[i][:2], self.layout[i][2], name.get_width() + 10))

        pass
