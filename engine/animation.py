
import math


class Animation():
    # _SPECS = dict(
    #     duration=1.0,
    #     delay=0.0,
    #     transition=Transition.linear,
    #     reverse=False,
    #     on_end=None,
    # )
    _SPECS = ['duration', 'delay', 'transition', 'reverse', 'on_end']

    def __init__(self, **kwargs):
        #specs
        # for attr, value in self._SPECS.items():
        #     setattr(self, attr, kwargs.pop(attr, value))
        self.duration = kwargs.pop('duration', 1.0)
        self.delay = kwargs.pop('delay', 0.0)
        self.transition = kwargs.pop('transition', Transition.linear)
        self.reverse = kwargs.pop('reverse', False)
        self.on_end = kwargs.pop('on_end', None)
        #props
        self.props = dict()
        for prop, target_value in kwargs.items():
            self.props[prop] = target_value

    def overwrite(self, **kwargs):
        #specs
        for attr in self._SPECS:
            if attr in kwargs:
                setattr(self, attr, kwargs.pop(attr))
        #props
        for prop, target_value in kwargs.items():
            self.props[prop] = target_value

    def __and__(self, other):
        if isinstance(other, dict):
            new = dict({
                'duration': self.duration,
                'delay': self.delay,
                'transition': self.transition,
                'reverse': self.reverse,
            }, **self.props)
            new.update(**other)
            return Animation(**new)
        return self


class Transition():

    @staticmethod
    def linear(t):
        return t

    @staticmethod
    def easeInQuad(t):
        return t**2

    @staticmethod
    def easeOutQuad(t):
        return -t * (t-2)

    @staticmethod
    def easeInOutQuad(t):
        if t < 0.5:
            return 2 * t**2
        else:
            t = 2*t - 1
            return -0.5 * (t*(t-2) - 1)

    @staticmethod
    def easeInCubic(t):
        return t**3

    @staticmethod
    def easeOutCubic(t):
        t -= 1
        return t**3 + 1

    @staticmethod
    def easeInOutCubic(t):
        t *= 2
        if t < 1:
            return 0.5 * t**3
        else:
            t -= 2
            return 0.5 * (t**3 + 2)

    @staticmethod
    def easeInQuart(t):
        return t**4

    @staticmethod
    def easeOutQuart(t):
        t -= 1
        return -(t**4 - 1)

    @staticmethod
    def easeInOutQuart(t):
        t *= 2
        if t < 1:
            return 0.5 * t**4
        else:
            t -= 2
            return -0.5 * (t**4 - 2)

    @staticmethod
    def easeInQuint(t):
        return t**5

    @staticmethod
    def easeOutQuint(t):
        t -= 1
        return t**5 + 1

    @staticmethod
    def easeInOutQuint(t):
        t *= 2
        if t < 1:
            return 0.5 * t**5
        else:
            t -= 2
            return 0.5 * (t**5 + 2)

    @staticmethod
    def easeInSine(t):
        return -1 * math.cos(t * math.pi / 2) + 1

    @staticmethod
    def easeOutSine(t):
        return math.sin(t * math.pi / 2)

    @staticmethod
    def easeInOutSine(t):
        return -0.5 * (math.cos(math.pi * t) - 1)

    @staticmethod
    def easeInExpo(t):
        if t == 0:
            return 0
        else:
            return 2**(10 * (t - 1))

    @staticmethod
    def easeOutExpo(t):
        if t == 1:
            return 1
        else:
            return -(2 ** (-10 * t)) + 1

    @staticmethod
    def easeInOutExpo(t):
        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            t = t * 2
            if t < 1:
                return 0.5 * 2**(10 * (t - 1))
            else:
                t -= 1
                return 0.5 * (-1 * (2 ** (-10 * t)) + 2)

    @staticmethod
    def easeInCirc(t):
        return -1 * (math.sqrt(1 - t * t) - 1)

    @staticmethod
    def easeOutCirc(t):
        t -= 1
        return math.sqrt(1 - (t * t))

    @staticmethod
    def easeInOutCirc(t):
        t *= 2
        if t < 1:
            return -0.5 * (math.sqrt(1 - t**2) - 1)
        else:
            t = t - 2
            return 0.5 * (math.sqrt(1 - t**2) + 1)

    @staticmethod
    def easeInElastic(t, amplitude=None, period=None):
        if period is None:
            period = 0.3

        if amplitude is None:
            amplitude = 1

        if amplitude < 1:
            amplitude = 1
            s = period / 4
        else:
            s = period / (2 * math.pi) * math.asin(1 / amplitude)

        t -= 1
        return -1 * (amplitude * 2**(10*t) * math.sin( (t-s)*(2*math.pi) / period))

    @staticmethod
    def easeOutElastic(t, amplitude=None, period=None):
        if period is None:
            period = 0.3

        if amplitude is None:
            amplitude = 1

        if amplitude < 1:
            amplitude = 1
            s = period / 4
        else:
            s = period / (2 * math.pi) * math.asin(1 / amplitude)

        return amplitude * 2**(-10*t) * math.sin((t-s)*(2*math.pi / period)) + 1

    @staticmethod
    def easeInOutElastic(t, amplitude=None, period=None):
        if period is None:
            period = 0.5

        if amplitude is None:
            amplitude = 1

        if amplitude < 1:
            amplitude = 1
            s = period / 4
        else:
            s = period / (2 * math.pi) * math.asin(1 / amplitude)

        t *= 2
        if t < 1:
            t -= 1
            return -0.5 * (amplitude * 2**(10*t) * math.sin((t - s) * 2 * math.pi / period))
        else:
            t -= 1
            return amplitude * 2**(-10*t) * math.sin((t - s) * 2 * math.pi / period) * 0.5 + 1

    @staticmethod
    def easeInBack(t, s=1.70158):
        return t**2 * ((s + 1) * t - s)

    @staticmethod
    def easeOutBack(t, s=1.70158):
        t -= 1
        return t**2 * ((s + 1) * t + s) + 1

    @staticmethod
    def easeInOutBack(t, s=1.70158):
        t *= 2
        if t < 1:
            s *= 1.525
            return 0.5 * (t * t * ((s + 1) * t - s))
        else:
            t -= 2
            s *= 1.525
            return 0.5 * (t * t * ((s + 1) * t + s) + 2)

    @staticmethod
    def easeInBounce(t):
        return 1 - Transition.easeOutBounce(1 - t)

    @staticmethod
    def easeOutBounce(t):
        if t < (1/2.75):
            return 7.5625 * t * t
        elif t < (2/2.75):
            t -= (1.5/2.75)
            return 7.5625 * t * t + 0.75
        elif t < (2.5/2.75):
            t -= (2.25/2.75)
            return 7.5625 * t * t + 0.9375
        else:
            t -= (2.65/2.75)
            return 7.5625 * t * t + 0.984375

    @staticmethod
    def easeInOutBounce(t):
        if t < 0.5:
            return Transition.easeInBounce(2 * t) * 0.5
        else:
            return Transition.easeOutBounce(2 * t - 1) * 0.5 + 0.5

