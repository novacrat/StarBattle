

class Particles:
    _time_after_birth = 0.0

    def __init__(self, **kwargs):
        self.particles = list()
        self.produce_rate = kwargs.pop('rate', None)
        self.produce_at_once = kwargs.pop('at_once', 1)
        self.produce_interval = 1.0 / self.produce_rate if self.produce_rate is not None else None
        if 'lifespan' in kwargs:
            self.Particle.DEFAULT_LIFESPAN = kwargs.pop('lifespan')

    def produce(self, dt, **kwargs):
        if self.produce_rate is None:
            for i in range(0, self.produce_at_once):
                self.particles.append(self.Particle(**kwargs))
        else:
            if self._time_after_birth > self.produce_interval:
                for i in range(0, self.produce_at_once):
                    self.particles.append(self.Particle(**kwargs))
                self._time_after_birth = 0.0
            else:
                self._time_after_birth += dt

    def progress(self, dt):
        # Process and detect expired
        expire = list()
        for particle in self.particles:
            if particle.lifetime >= particle.lifespan:
                expire.append(particle)
            else:
                particle.progress(dt)
        for particle in expire:
            self.particles.remove(particle)

    class Particle():
        DEFAULT_LIFESPAN = 1.0

        lifespan = DEFAULT_LIFESPAN
        lifetime = 0.0
        t = 0.0

        def __init__(self, **kwargs):
            self.lifespan *= kwargs.pop('lifespan', self.DEFAULT_LIFESPAN)

        def progress(self, dt):
            self.lifetime += dt
            self.t = self.lifetime / self.lifespan

