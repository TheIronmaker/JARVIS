# Implements a second-order critically damped response as described in SmoothDamp docs
import numpy as np

class SmoothDamp:
    def __init__(self, base=0.0, y_vel=0.0, acc=0.0, eps=0.001):
        self.eps = eps

        # State
        self.xp = base
        self.y = base
        self.y_vel = y_vel
        self.acc = acc

        # Parameters
        self.k1 = 0.0
        self.k2 = 0.0
        self.k3 = 0.0
        self.T = 0.01

    def update_k(self, f, z, r):
        """Recompute k values from frequency/damping parameters."""
        f = max(f, 1e-6)

        self.k1 = z / (np.pi * f)
        self.k2 = 1.0 / (2.0 * np.pi * f) ** 2
        self.k3 = r * z / (2.0 * np.pi * f)

    def next(self, x, x_vel=None):
        """Advance the smooth damp by one timestep."""

        T = self.T if self.T != 0 else 0.01

        # Infer input velocity if needed
        if x_vel is None: x_vel = (x - self.xp) / T

        # Store previous input
        self.xp = x

        # Clamp k2 for stability
        k2 = max(self.k2, 0.25 * T * T)

        # Acceleration
        self.acc = (x + self.k3 * x_vel - self.y - self.k1 * self.y_vel) / k2

        # Dead-zone (apply BEFORE integration)
        if abs(self.acc) < self.eps and abs(self.y_vel) < self.eps:
            self.acc = 0.0
            self.y_vel = 0.0

        # Semi-implicit Euler integration
        self.y_vel += T * self.acc
        self.y += T * self.y_vel

        return self.y

class SmoothDampArray:
    def __init__(self, size, base=None, x_vel=0, acc=0, eps=0.001):
        self.size = size
        self.eps = eps

        self.defaults = np.zeros((*size, 4))
        self.defaults[..., 3] = 0.01
        self.k = np.zeros((*size, 3))

        # Data Columns: [previous_x, y, y_vel, acceleration]
        self.data = np.zeros((*size, 4))
        for i, var in enumerate([base, base, x_vel, acc]):
            self.data[..., i] = var if var is not None else 0
        
        self.update_k()

    def update_k(self, loc=...):
        """ Finds K values, and updates all values, or a specific location if given"""
        f = np.maximum(self.defaults[loc, 0], 1e-6)
        z = self.defaults[loc, 1]
        r = self.defaults[loc, 2]

        self.k[loc, 0] = z / (np.pi * f)
        self.k[loc, 1] = 1.0 / (2 * np.pi * f) ** 2
        self.k[loc, 2] = r * z / (2 * np.pi * f)
    
    def update_defaults(self, f=None, z=None, r=None, T=None, loc: slice | tuple=..., update_k=True):
        """Updates one or all f, z, or r presets and recalculates """
        params = [f, z, r, T]
        if all(p is None for p in params): return

        for i, var in enumerate(params):
            if var is not None:
                self.defaults[loc, i] = var
        
        if update_k: self.update_k(loc=loc)

    def next(self, x, x_vel=None, loc: slice | tuple=..., update=False):
        """
        Update smooth damp at location(s)
        Args:
            x: Input value(s)
            x_vel: Input velocity (optional, calculated if None)
            loc: Location to update, or None for all
        """

        T = np.where(self.defaults[loc, 3] != 0, self.defaults[loc, 3], 0.01)
        k1, k2, k3 = self.k[loc, 0], np.maximum(self.k[loc, 1], 0.25 * T * T), self.k[loc, 2]
        xp, y, y_vel, acc = [self.data[loc, i] for i in range(4)]

        # Find x_vel if not provided
        if x_vel is None: x_vel = (x - xp) / T

        # Smooth damp calculations
        self.data[loc, 0] = x
        acc = (x + k3 * x_vel - y - k1 * y_vel) / k2

        # Clamp dead-zone before integrating
        mask = (np.abs(acc) < self.eps) & (np.abs(y_vel) < self.eps)

        acc = np.where(mask, 0, acc)
        y_vel = np.where(mask, 0, y_vel)

        # Integrate semi-implicit Euler
        y_vel += T * acc
        y += T * y_vel

        # Save data
        self.data[loc, 1:4] = np.stack((y, y_vel, acc), axis=-1)

        if update:
            x = y
        return y
    
    def current(self, indexes="all", loc: slice | tuple=...):
        """Get current state at location(s)"""
        readout = {"xp":0, "y":1, "y_vel":2, "acc":3}
        if isinstance(indexes, str): indexes = [indexes]

        if indexes == "all": return {name: self.data[loc, i] for name, i in readout.items()}
        return {name: self.data[loc, readout[name]] for name in indexes if name in readout}
