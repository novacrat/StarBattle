
import math, numpy


class Gradient:

    @staticmethod
    def cast(value):
        if value is None or isinstance(value, (bool, str)):
            raise Exception('Insufficient value for gradient')
        elif isinstance(value, (list, tuple)):
            return numpy.asarray(value)
        else:
            return value

    @staticmethod
    def is_casted_equal(a, b):
        if isinstance(a, (numpy.ndarray)):
            return (a == b).all()
        else:
            return a == b

    def _append_stop(self, t, next_t, value, next_value, transition=None):
        # prepare values
        if isinstance(value, (list, tuple)):
            value = numpy.asarray(value)
        if isinstance(next_value, (list, tuple)):
            next_value = numpy.asarray(next_value)
        # prepare increment
        t_increment = next_t - t
        increment = None if next_value is None or self.is_casted_equal(value, next_value) else next_value - value
        self.stops.append((t, next_t, value, next_value, increment, t_increment, None))

    def __init__(self, spec):
        # Items contains tuples:
        # t, next_t, value, next_value, increment, t_increment, transition
        self.stops = list()
        self.cache = dict()

        # Spec as list? Equal stops than
        if isinstance(spec, (tuple, list)):
            i, t_increment = 0, 1.0 / (len(spec)-1)
            while i < len(spec)-1:
                self._append_stop(i * t_increment, (i + 1) * t_increment, spec[i], spec[i + 1])
                i += 1

        # Spec as dict? Get stops from dictionary keys than
        elif isinstance(spec, dict):
            value, t = None, None
            for next_t, next_value in spec.items():
                next_value = self.cast(next_value)
                # 1st stop?
                if t is None:
                    # Append planar first step
                    if next_t > 0.0:
                        self._append_stop(0.0, next_t, next_value, None)
                    elif next_t < 0.0:
                        raise Exception("Gradient step beyond limits")
                else:
                    if next_t <= t:
                        raise Exception("Gradient steps collision")
                    self._append_stop(t, next_t, value, next_value)
                # prepare next iteration
                t, value = next_t, next_value
            # Last stop
            if next_t < 1.0:
                self._append_stop(t, 1.0, next_value, None)
            if t > 1.0:
                raise Exception("Gradient step beyond limits")

        else:
            raise Exception('Insufficient gradient spec')

        if not self.stops:
            raise Exception('Insufficient gradient stops amount')

        # print(self.stops)

    def fetch_value(self, t):
        # Last value?
        if t >= 1.0:
            return self.stops[-1][2]

        # Determine current stop
        stop = None
        for stop in self.stops:
            if stop[0] <= t < stop[1]:
                break

        # Normalize t increment
        if stop[4] is None:
            value = stop[2]
        else:
            nt = (t - stop[0]) / stop[5]
            value = stop[2] + stop[4] * nt

        return value

    def fetch_cached_value(self, t):
        cache_t = int(t*100)
        if cache_t in self.cache:
            return self.cache[cache_t]

        # Last value?
        if t >= 1.0:
            return self.stops[-1][2]

        # Determine current stop
        stop = None
        for stop in self.stops:
            if stop[0] <= t < stop[1]:
                break

        # Normalize t increment
        if stop[4] is None:
            value = stop[2]
        else:
            nt = (t - stop[0]) / stop[5]
            value = stop[2] + stop[4] * nt

        self.cache[cache_t] = value
        return value

