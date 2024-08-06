
import pygame, numpy
from . import animation as mod_animation


class Viewer:
    dt = 0
    BACKGROUND_COLOR = (0,0,0)
    WIDTH = 1024
    HEIGHT = 680

    class _AnimatorAide:
        CANCEL = 1
        END = 2
        status = None

        def __init__(self, animation: mod_animation.Animation):
            self.on_end = animation.on_end

        def cancel(self):
            self.status = self.CANCEL

        def end(self):
            self.status = self.END

        def __del__(self):
            if self.status == self.END:
                if self.on_end is not None:
                    self.on_end()

    def __init__(self, srf=None):
        if srf is None:
            pygame.init()
            flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.HWACCEL
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), flags)
        else:
            self.screen = srf

        self._animators = dict()
        self._animators_aides = dict()
        self.views = list()

    def _fetch_animator(self, easing_function, initial_value, target_value, duration, delay=0.0):
        # convert list and tuples to array, so we can operate them
        if isinstance(initial_value, (list, tuple)) or isinstance(target_value, (list, tuple)):
            initial_value = numpy.asarray(initial_value)
            target_value = numpy.asarray(target_value)

        value = initial_value
        inc = target_value - initial_value
        # Delay with initial value
        t = 0.0
        while t < delay:
            yield value
            t += self.dt / duration
        # Progress value
        t = 0.0
        while True:
            yield value
            t += self.dt / duration
            if t < 1.0:
                value = inc * easing_function(t) + initial_value
            else:
                return target_value

    def set_screen(self, screen_surface):
        self.screen = screen_surface

    def get_screen(self) -> pygame.SurfaceType:
        return self.screen

    def set_animation(self, view, animation: mod_animation.Animation):
        aide = self._AnimatorAide(animation)
        # Get current value
        for prop, target_value in animation.props.items():

            # for truly initial
            if prop[:3] != '___':
                # fetch explicit initial value
                if '___'+prop in animation.props:
                    initial_value = animation.props['___'+prop]
                else:
                    # fetch initial value from view
                    try:
                        initial_value = getattr(view, prop)
                    except AttributeError:
                        # skip this prop for this animation
                        continue

                # copy mutable
                if isinstance(initial_value, (tuple, list)):
                    initial_value = initial_value[:]
                elif isinstance(initial_value, dict):
                    initial_value = initial_value.copy()

                if animation.reverse:
                    target_value, initial_value = initial_value, target_value

                # Mark as canceled previous animator
                if (view, prop) in self._animators:
                    animator = self._animators[(view, prop)]
                    self._animators_aides[animator].cancel()
                    del self._animators_aides[animator]

                # Register new animator
                animator = self._fetch_animator(
                    animation.transition, initial_value, target_value, animation.duration, animation.delay
                )
                self._animators[(view, prop)] = animator
                self._animators_aides[animator] = aide
        pass

    def cancel_animation(self, view=None, prop=None):
        pass

    def progress_animation(self, view=None, prop=None):
        completed = list()
        for (a_view, a_prop), animator in self._animators.items():
            # TODO: here could be the check for animation progression
            try:
                setattr(a_view, a_prop, next(animator))
            except StopIteration as e:
                setattr(a_view, a_prop, e.value)
                completed.append((a_view, a_prop))
                self._animators_aides[animator].end()
                del self._animators_aides[animator]
        for i in completed:
            self._animators.pop(i)

    def is_animated(self, view=None):
        if view is None:
            return not not self._animators
        else:
            for (a_view, a_prop) in self._animators:
                if view is a_view:
                    return True
            return False

    def attach(self, view):
        self.views.append(view)

    def detach(self, view):
        self.views.remove(view)

    def attach_after(self, view, view_to_attach):
        i = self.views.index(view)
        self.views.insert(i + 1, view_to_attach)

    def attach_before(self, view, view_to_attach):
        i = self.views.index(view)
        self.views.insert(i, view_to_attach)

    def progress(self, dt):
        self.dt = dt
        for view in self.views:
            view.progress(self.dt)
        self.progress_animation()

    def draw(self, srf: pygame.SurfaceType=None):
        draw_surface = self.screen if srf is None else srf
        draw_surface.fill(self.BACKGROUND_COLOR)
        for view in self.views:
            view.draw(draw_surface)
        pygame.display.flip()

    @staticmethod
    def dealpha(srf: pygame.SurfaceType, opaque, simple=True):
        array = pygame.surfarray.pixels_alpha(srf)
        if simple:
            alpha = 255 - int(opaque * 255)
            array[array < alpha] = 0
            array[array >= alpha] -= alpha
        else:
            array[...] = (array[...] * opaque).astype(numpy.uint8)
        del array

    @staticmethod
    def darken(srf: pygame.SurfaceType, darken, simple=True):
        array = pygame.surfarray.pixels_red(srf)
        if simple:
            factor = 255 - int(darken * 255)
            array[array < factor] = 0
            array[array >= factor] -= factor
        else:
            array[...] = (array[...] * darken).astype(numpy.uint8)
        del array


class View:
    visible = True
    visible_animated = True
    progressive = False

    def __init__(self, viewer):
        pass

    def animate(self, *args, **kwargs):
        for animation in args:
            if isinstance(animation, mod_animation.Animation):
                theViewer.set_animation(self, animation)
        if kwargs:
            theViewer.set_animation(self, mod_animation.Animation(**kwargs))

    def progress(self, dt):
        if self.progressive:
            self._progress(dt)

    def draw(self, srf: pygame.SurfaceType):
        if self.visible or (self.visible_animated and theViewer.is_animated(self)):
            self._draw(srf)

    def _progress(self, dt):
        pass

    def _draw(self, srf: pygame.SurfaceType):
        pass


theViewer = Viewer()