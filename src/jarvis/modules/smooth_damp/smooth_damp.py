import numpy as np

class SmoothDamp():
    def __init__(self, base=0, dy=0, acc=0, rounding=None):
        self.rounding = rounding

        self.T = 0.01

        self.xp = base
        self.y = base
        self.dy = dy
        self.acc = acc

        self.k1, self.k2, self.k3 = 0, 0, 0

    def find_k(self, f, z, r):
        self.k1 = z / (np.pi * f)
        self.k2 = 1 / ((2 * np.pi * f) * (2 * np.pi * f))
        self.k3 = r * z / (2 * np.pi * f)

    def update(self, x, xd=None):
        if xd == None:
            xd = (x - self.xp) / self.T
            self.xp = x

        self.y = self.y + self.T * self.dy
        self.acc = (x + self.k3 * xd - self.y - self.k1 * self.dy) / self.k2
        value = self.dy + self.T * self.acc
        self.dy = round(value, self.rounding) if self.rounding else value

        # Flatten dy Noise
        if abs(self.dy) <= 0.001: self.dy = 0

        return self.y
        