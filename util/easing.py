"""
Input is a list called 't'. Output is a list called 't'
The last line right now is 't = [linear(t_) for t_ in t]'
Choose the function you want to call and replace 'linear'
"""
import math


def linear(t):
    return t


def easeInQuad(t):
    return t**2


def easeOutQuad(t):
    return -t * (t-2)


def easeInOutQuad(t):
    if t < 0.5:
        return 2 * t**2
    else:
        t = 2*t - 1
        return -0.5 * (t*(t-2) - 1)


def easeInCubic(t):
    return t**3


def easeOutCubic(t):
    t -= 1
    return t**3 + 1


def easeInOutCubic(t):
    t *= 2
    if t < 1:
        return 0.5 * t**3
    else:
        t -= 2
        return 0.5 * (t**3 + 2)


def easeInQuart(t):
    return t**4


def easeOutQuart(t):
    t -= 1
    return -(t**4 - 1)


def easeInOutQuart(t):
    t *= 2
    if t < 1:
        return 0.5 * t**4
    else:
        t -= 2
        return -0.5 * (t**4 - 2)


def easeInQuint(t):
    return t**5


def easeOutQuint(t):
    t -= 1
    return t**5 + 1


def easeInOutQuint(t):
    t *= 2
    if t < 1:
        return 0.5 * t**5
    else:
        t -= 2
        return 0.5 * (t**5 + 2)


def easeInSine(t):
    return -1 * math.cos(t * math.pi / 2) + 1


def easeOutSine(t):
    return math.sin(t * math.pi / 2)


def easeInOutSine(t):
    return -0.5 * (math.cos(math.pi * t) - 1)


def easeInExpo(t):
    if t == 0:
        return 0
    else:
        return 2**(10 * (t - 1))


def easeOutExpo(t):
    if t == 1:
        return 1
    else:
        return -(2 ** (-10 * t)) + 1


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


def easeInCirc(t):
    return -1 * (math.sqrt(1 - t * t) - 1)


def easeOutCirc(t):
    t -= 1
    return math.sqrt(1 - (t * t))


def easeInOutCirc(t):
    t *= 2
    if t < 1:
        return -0.5 * (math.sqrt(1 - t**2) - 1)
    else:
        t = t - 2
        return 0.5 * (math.sqrt(1 - t**2) + 1)


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


def easeInBack(t, s=1.70158):
    return t**2 * ((s + 1) * t - s)


def easeOutBack(t, s=1.70158):
    t -= 1
    return t**2 * ((s + 1) * t + s) + 1


def easeInOutBack(t, s=1.70158):
    t *= 2
    if t < 1:
        s *= 1.525
        return 0.5 * (t * t * ((s + 1) * t - s))
    else:
        t -= 2
        s *= 1.525
        return 0.5 * (t * t * ((s + 1) * t + s) + 2)


def easeInBounce(t):
    return 1 - easeOutBounce(1 - t)


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


def easeInOutBounce(t):
    if t < 0.5:
        return easeInBounce(2*t) * 0.5
    else:
        return easeOutBounce(2*t - 1) * 0.5 + 0.5

