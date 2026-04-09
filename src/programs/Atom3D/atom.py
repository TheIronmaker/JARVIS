#! atom.py

# System imports
import numpy as np
import math

class Atom:
    def __init__(self, config):
        self.orbital = config['orbital']
        self.n = self.orbital['n']
        self.l = self.orbital['l']
        self.m = self.orbital['m']
        self.N = self.orbital['N']

        self.a0 = 1.0
        self.electron_r = config['electron_r']
        self.hbar = 1
        self.m_e = 1
        self.dt = 0.5
        
        self.particles = np.zeros((self.N), dtype=[('pos', 'f4', (3,)), ('color', 'f4', (4,)), ('vel', 'f4', (3,))])

    def get_orbitals(self):
        return self.n, self.l, self.m, self.N, self.electron_r

    def set_orbitals(self, n, l, m, N=None, electron_r=None):
        """ Update orbital parameters and regenerate particles. """
        self.n = n
        self.l = l
        self.m = m
        self.N = N if N is not None else self.N
        self.electron_r = electron_r if electron_r is not None else self.electron_r
        self.generateParticles()

    def sphericalToCartesian(self, r:np.ndarray, theta:np.ndarray, phi:np.ndarray) -> np.ndarray:
        """
        Convert spherical coordinates (r, theta, phi) to Cartesian coordinates (x, y, z).
        Args:
            r: radial distance
            theta: polar angle (0 to pi)
            phi: azimuthal angle (0 to 2pi)
        Returns:
            numpy array of size (N, 3) Cartesian coordinates.
        """
        return np.stack((
            r * np.sin(theta) * np.cos(phi),
            r * np.cos(theta),
            r * np.sin(theta) * np.sin(phi)),
            axis=-1).astype(np.float32)
            # The axis flip give shape [N, 3] instead of [3, N]

    def sampleR(self) -> np.ndarray:
        # Does not take arrays of n, l, or a0 since math.factorial does not support that.
        # scipy.special.factorial handles arrays, but is slower for large n-l values
        n = self.n
        l = self.l
        a0 = self.a0

        # Setup Variables
        N = 4096
        rMax = 10.0 * n**2 * a0
        r = np.linspace(0, rMax, N, dtype=np.float32)
        rho = 2.0 * r / (n * a0)

        # Associated Laguerre L_{n-l-1}^{2l+1}(rho)
        k = n - l - 1
        alpha = 2 * l + 1
        L = np.ones(N, dtype=np.float32)
        Lm1 = 1.0 + alpha - rho
        if k == 1: L = Lm1
        elif k > 1:
            Lm2 = np.ones(N, dtype=np.float32)
            for i in range(2, k + 1):
                L = ((2 * i - 1 + alpha - rho) * Lm1 - (i - 1 + alpha) * Lm2) / i
                Lm2, Lm1 = Lm1, L
        
        # norm is a scalar based on orbitals and may be calculated for multiple functions at once and saved as self.norm
        # norm = (2/(n*a0))**3 * math.factorial(n-l-1) / (2*n*math.factorial(n+l))
        # L and R are arrays of shape (N,), and numpy handles the operations correctly.
        R = np.sqrt(self.norm) * np.exp(-rho / 2.0) * rho**l * L

        pdf = R**2 * r**2
        cdf = np.cumsum(pdf)
        cdf /= cdf[-1]

        # u = random number in [0, 1] for each particle, shape (N,)
        rng = np.random.default_rng()
        u = rng.random(size=self.N, dtype=np.float32)
        idx = np.searchsorted(cdf, u)
        return idx * (rMax / (N - 1))
        # Option: return np.interp(rng.random(N), cdf, r)

    def sampleTheta(self) -> np.ndarray:
        l = self.l
        m = self.m

        N = 2048
        dtheta = np.pi / (N - 1)
        theta = np.linspace(0, np.pi, N, dtype=np.float32)
        x = np.cos(theta)
        
        Pmm = np.ones(N, dtype=np.float32)
        if m > 0:
            somx2 = np.sqrt((1-x)*(1+x))
            fact = 1
            for _ in range(1, m + 1):
                Pmm *= -fact * somx2
                fact += 2

        if l == m:
            Plm = Pmm
        else:
            Pm1m = x * (2 * m + 1) * Pmm
            if l != m + 1:
                for ll in range(m + 2, l + 1):
                    Pll = ((2 * ll - 1) * x * Pm1m - (ll + m - 1) * Pmm) / (ll - m)
                    Pmm, Pm1m = Pm1m, Pll
            Plm = Pm1m

        pdf = np.sin(theta) * Plm**2
        cdf = np.cumsum(pdf)
        cdf /= cdf[-1]

        rng = np.random.default_rng()
        u = rng.random(size=self.N, dtype=np.float32)
        idx = np.searchsorted(cdf, u)
        return idx * dtheta
        # Option B (smoother interpolation for 3D): return np.interp(rng.random(self.N), cdf, theta)
    
    def samplePhi(self) -> np.ndarray:
        rng = np.random.default_rng()
        return 2 * math.pi * rng.random(size=self.N, dtype=np.float32)

    def heatmap_fire(self, values) -> np.ndarray:
        values = np.clip(values, 0.0, 1.0)

        colors = np.array([
                [0.0, 0.0, 0.0, 1],  # 0.0 Black
                [0.5, 0.0, 0.99, 1], # 0.2 Dark Purple
                [0.8, 0.0, 0.0, 1],  # 0.4 Deep Red
                [1.0, 0.5, 0.0, 1],  # 0.6 Orange
                [1.0, 1.0, 0.0, 1],  # 0.8 Yellow
                [1.0, 1.0, 1.0, 1]]) # 1.0 White

        id = [(i)/5 for i in range(0, 6)]
        return np.column_stack([np.interp(values, id, colors[:, i]) for i in range(0, 4)])

    def inferno(self, r, theta, phi) -> np.ndarray:
        """ Colorization for particles using array based calculations """
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
        return self.heatmap_fire(intensity * 1.5 * 5**n)

    def generateParticles(self, N=None):
        n = self.n
        l = self.l
        a0 = self.a0
        if N: self.N = N

        self.norm = (2/(n*a0))**3 * math.factorial(n-l-1) / (2*n*math.factorial(n+l))
        
        # Calculate all Cartesian coordinates at once using numpy arrays for better performance
        pos = self.sphericalToCartesian(
            self.sampleR(),
            self.sampleTheta(),
            self.samplePhi())

        #@[docs]@revisit
        # pos is of shape (N, 3) where pos[:, 0] is all x positions, pos[:, 1] is all y positions, and pos[:, 2] is all z positions.
        r = np.linalg.norm(pos, axis=1)
        theta = np.arccos(np.clip(pos[:, 1] / r, -1.0, 1.0)) # avoids division by zero and ensures valid input for arccos
        phi = np.arctan2(pos[:, 2], pos[:, 0])

        self.particles = np.zeros((self.N), dtype=[('pos', 'f4', (3,)), ('color', 'f4', (4,)), ('vel', 'f4', (3,))])
        self.particles['pos'] = pos
        self.particles['color'] = self.inferno(r, theta, phi)
        self.particles['vel'] = np.zeros((self.N, 3), dtype=np.float32)
    
    def calculateProbabilityFlow(self, particles) -> np.ndarray:
        r = np.linalg.norm(particles, axis=1).clip(1e-6, None)
        theta = np.arccos(particles[:, 1] / r)
        phi = np.arctan2(particles[:, 2], particles[:, 0])

        sinTheta = np.sin(theta)
        if np.any(np.abs(sinTheta) < 1e-4): sinTheta = np.clip(sinTheta, 1e-4, None)
        v_mag = self.hbar * self.m / (self.m_e * r * sinTheta)

        vx = -v_mag * np.sin(phi)
        vy = np.zeros(phi.shape, dtype=np.float32)
        vz = v_mag * np.cos(phi)

        return np.column_stack([vx, vy, vz])

    def updateVelocities(self):
        r = np.linalg.norm(self.particles['pos'], axis=1).clip(1e-6, None)
        theta = np.arccos(self.particles['pos'][:, 1] / r)

        self.particles['vel'] = self.calculateProbabilityFlow(self.particles['pos'])
        temp_pos = self.particles['pos'] + self.particles['vel'] * self.dt
        new_phi = np.arctan2(temp_pos[:, 2], temp_pos[:, 0])
        self.particles["pos"] = self.sphericalToCartesian(r, theta, new_phi)

        return self.particles

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    config = {
        "orbital": {"n": 3, "l": 2, "m": 1, "N": 10000},
        "electron_r": 1
    }

    atom = Atom(config)
    atom.generateParticles()

    x, y, z = atom.particles['pos'].T
    colors = atom.particles['color']
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=colors, s=20) 
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()