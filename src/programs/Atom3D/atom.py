#! atom.py

# System imports
import numpy as np
from scipy.special import factorial
from scipy.stats import norm
import math
import random

import time

# Specific imports
import glm

class Atom:
    def __init__(self, config):
        self.orbital = config['orbital']
        self.N = config['N']
        self.n = self.orbital['n']
        self.l = self.orbital['l']
        self.m = self.orbital['m']

        self.a0 = 1.0
        self.electron_r = config['electron_r']
        
        self.particles = np.zeros((self.N, 6), dtype=np.float32)

    def sphericalToCartesian(self, r:np.ndarray, theta:np.ndarray, phi:np.ndarray) -> np.ndarray:
        """
        Convert spherical coordinates (r, theta, phi) to Cartesian coordinates (x, y, z).
        r: radial distance
        theta: polar angle (0 to pi)
        phi: azimuthal angle (0 to 2pi)
        Returns an (N, 3) numpy array of Cartesian coordinates.
        """
        return np.stack((
            r * np.sin(theta) * np.cos(phi),
            r * np.cos(theta),
            r * np.sin(theta) * np.sin(phi)),
            axis=-1).astype(np.float32)

    def sampleR(self) -> np.ndarray:
        # Does not take arrays of n, l, or a0 since math.factorial does not support that.
        # scipy.special.factorial handles arrays, but is slower for large n-l values
        n = self.n
        l = self.l
        a0 = self.a0

        N = 4096
        rMax = 10.0 * n**2 * a0
        dr = rMax / (N - 1)
        r = np.linspace(0, rMax, N, dtype=np.float32)
        rho = 2 * r / (n * a0)

        # Associated Laguerre L_{n-l-1}^{2l+1}(rho)
        k = n - l - 1
        alpha = 2 * l + 1

        L = np.ones(N, dtype=np.float32)
        Lm1 = 1 + alpha - rho
        if k == 1: L = Lm1
        elif k > 1:
            Lm2 = np.ones(N, dtype=np.float32)
            for i in range(2, k + 1):
                L = ((2 * i - 1 + alpha - rho) * Lm1 - (i - 1 + alpha) * Lm2) / i
                Lm2, Lm1 = Lm1, L
        
        # norm is a scalar based on orbitals and may be calculated for multiple functions at once and saved as self.norm
        # norm = (2/(n*a0))**3 * math.factorial(n-l-1) / (2*n*math.factorial(n+l))
        # L and R are arrays of shape (N,), and numpy handles the operations correctly.
        R = np.sqrt(self.norm) * np.exp(-rho / 2) * rho**l * L

        pdf = R**2 * r**2 * dr
        cdf = np.cumsum(pdf)
        cdf /= cdf[-1]

        # u = random number in [0, 1] for each particle, shape (N,)
        u = np.random.random(size=self.N)
        idx = np.searchsorted(cdf, u).astype(np.float32)
        return idx * dr

    def sampleTheta(self) -> np.ndarray:
        l = self.l
        m = self.m

        N = 2048
        dtheta = np.pi / (N - 1)
        theta = np.linspace(0, np.pi, N, dtype=np.float32) * dtheta
        x = np.cos(theta)
        
        Pmm = np.ones(N, dtype=np.float32)
        if m > 0:
            somx2 = np.sqrt((1-x)*(1+x))
            fact = 1
            for _ in range(1, m + 1):
                Pmm *= -fact * somx2
                fact += 2

        Plm = Pmm
        if l != m:
            Pm1m = x * (2 * m + 1) * Pmm
            if l != m + 1:
                for ll in range(m + 2, l + 1):
                    Pll = ((2 * ll - 1) * x * Pm1m - (ll + m - 1) * Pmm) / (ll - m)
                    Pmm, Pm1m = Pm1m, Pll
            Plm = Pm1m

        pdf = np.sin(theta) * Plm**2
        cdf = np.cumsum(pdf)
        cdf /= cdf[-1]

        u = np.random.random(size=self.N)
        idx = np.searchsorted(cdf, u).astype(np.float32)
        return idx * dtheta
    
    def samplePhi(self) -> np.ndarray:
        return 2 * math.pi * np.random.random(size=self.N)
    
    def heatmap_fire(self, values) -> np.ndarray:
        result = np.zeros((4), dtype=np.float32)
 
        return result

    def inferno(self, r, theta, phi) -> np.ndarray:
        """ Colorization for particles using array based calculations
        Args:
          r = np.linalg.norm(pos) Shape: (N,) coor: x, y, z

        """
        
        n = self.n
        l = self.l
        m = self.m
        N = self.N
        a0 = self.a0

        # r, theta, phi are all (N,) arrays. n, l, m are scalars
        rho = 2 * r / (n * a0)
        k = n - l - 1
        alpha = 2 * l + 1

        L = np.ones(N, dtype=np.float32)
        if k == 1:
            L += alpha - rho
        elif k > 1:
            Lm2 = np.ones(N, dtype=np.float32)
            Lm1 = 1 + alpha - rho
            for i in range(2, k + 1):
                L = ((2 * i - 1 + alpha - rho) * Lm1 - (i - 1 + alpha) * Lm2) / i
                Lm2, Lm1 = Lm1, L
        
        # norm is a scalar base on orbitals and may be calculated for multiple functions at once and saved as self.norm
        # norm = (2/(n*a0))**3 * math.factorial(n-l-1) / (2*n*math.factorial(n+l))
        R = math.sqrt(self.norm) * np.exp(-rho/2) * rho**l * L
        radial = R**2

        x = np.cos(theta)

        Pmm = np.ones(N, dtype=np.float32)        
        if m > 0:
            somx2 = np.sqrt((1 - x) * (1 + x))
            for fact in range(1, 2*m, 2):
                Pmm *= -fact * somx2
        
        Plm = Pmm
        if l != m:
            Pm1m = x * (2 * m + 1) * Pmm
            if l == m + 1:
                Plm = Pm1m
            else:
                for ll in range(m + 2, l + 1):
                    Pll = ((2 * ll - 1) * x * Pm1m - (ll + m - 1) * Pmm) / (ll - m)
                    Pmm, Pm1m = Pm1m, Pll
                Plm = Pm1m
        
        angular = Plm**2
        intensity = radial * angular

        # May add config values for scaling
        return self.heatmap_fire(intensity * 1.5 * n**5)

    def inferno_single(self, r, theta, phi, n, l, m) -> np.ndarray:
        """
        Simple vectorized color mapping for particles.
        Maps radial distance `r` to a color ramp from blue (close) to red (far).    
        Returns an (N,4) numpy float32 array of RGBA values in [0,1].
        """

        rho = 2 * r / (self.n * self.a0)
        k = self.n - self.l - 1
        alpha = 2 * self.l + 1

        L = 1
        if k == 1:
            L = 1 + alpha - rho
        elif k > 1:
            Lm2 = 1
            Lm1 = 1 + alpha - rho
            for i in range(2, k + 1):
                L = ((2 * i - 1 + alpha - rho) * Lm1 - (i - 1 + alpha) * Lm2) / i
                Lm2, Lm1 = Lm1, L
        
        # N_nl = sqrt( (2/na_0)**3 * (n - l - 1)! / (2n * (n + l)!) )
        norm = np.sqrt((2 / (self.n * self.a0))**3 * factorial(self.n - self.l - 1) / (2 * self.n * factorial(self.n + self.l)))
        R = norm * np.exp(-rho / 2) * rho**self.l * L
        radial = R**2

        x = math.cos(theta)

        Pmm = 1
        if self.m > 0:
            somx = math.sqrt((1.0 - x) * (1.0 + x))
            fact = 1.0
            for i in range(1, self.m + 1):
                Pmm *= -fact * somx
                fact += 2.0
        
        Plm = None
        if self.l == self.m:
            Plm = Pmm
        else:
            Pmm1 = x * (2 * self.m + 1) * Pmm
            if self.l == self.m + 1:
                Plm = Pmm1
            else:
                for i in range(self.m + 2, self.l + 1):
                    Plm = ((2 * i - 1) * x * Pmm1 - (i + self.m - 1) * Pmm) / (i - self.m)
                    Pmm, Pmm1 = Pmm1, Plm

        angular = Plm**2

        #intensity = np.zeros(r.shape[0], dtype=np.float32)
        intensity = radial * angular
        return self.heatmap_fire(intensity * 1.5 * self.n**5)

    def generateParticles(self, n=None, l=None, m=None, N=None, a0=None):
        if n is not None: self.n = n
        if l is not None: self.l = l
        if m is not None: self.m = m
        if N is not None: self.N = N
        if a0 is not None: self.a0 = a0

        self.norm = (2/(n*a0))**3 * math.factorial(n-l-1) / (2*n*math.factorial(n+l))
        
        # Calculate all Cartesian coordinates at once using numpy arrays for better performance
        pos = self.sphericalToCartesian(
            self.sampleR(),
            self.sampleTheta(),
            self.samplePhi())

        ### Build col:
        # r = length of each vector in pos
        # theta = arccos of y value divided by r for each vector in pos | Improved to avoid division by zero and ensure valid input for arccos
        # phi = arctan2 of z and x values for each vector in pos
        # Recompute spherical coords (robust) and compute colors

        # Need array of linalg for each group of three values in pos, which is (N, 3)
        print("pos shape:", pos.shape)
        r = np.linalg.norm(pos)
        print("latest r:", r)
        # theta = np.arccos(pos[:, 1] / r) # Original | Must be valid input for arccos
        theta = np.arccos(np.clip(pos[1] / (r + 1e-12), -1.0, 1.0))
        phi = np.arctan2(pos[2], pos[0])
        col = self.inferno(r, theta, phi) # Shape: N, 4 (glm vec4 -> np vec4)

        # Store particles as list of (pos, color) tuples for downstream code
        self.particles = list(zip(pos.astype(np.float32), col.astype(np.float32)))


config = {
    "orbital": {"n": 4, "l": 2, "m": 1},
    "N": 10000,
    "electron_r": 1.5
}

atom = Atom(config)
#atom.generateParticles()

array = np.random.random((config["N"], 6)) * np.array([2.0, math.pi, 2*math.pi, 1.0, 1.0, 1.0])

st = time.time()
R = atom.sampleTheta()
et = time.time() - st
print("Milliseconds taken for sampleTheta:", et * 1000)

import matplotlib.pyplot as plt
plt.plot(R)

# Add a title and labels (optional but recommended)
plt.title("1D NumPy Array Visualization (Line Plot)")
plt.xlabel("Index")
plt.ylabel("Value")

# Display the plot
plt.show()