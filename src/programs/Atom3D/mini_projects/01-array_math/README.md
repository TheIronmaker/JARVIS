01 - Array Math (NumPy)
================================

Goals
- Learn NumPy arrays, broadcasting, ufuncs, vectorized transforms.
- Replace per-particle Python loops with bulk array operations.

Core concepts
- `numpy.ndarray` memory layout and shape
- Broadcasting rules and axis alignment
- Vectorized trig and linear algebra (matrix ops)
- Efficient conversions between spherical and cartesian representations

Plan
1. Implement a vectorized particle container: arrays for `r, theta, phi` and `x,y,z` conversions.
2. Implement batch spherical->cartesian and cartesian->spherical transforms using broadcasting.
3. Implement a vectorized phi update (apply many dphi at once) and convert once to Cartesian per-frame.
4. Build simple notebooks showing speed comparisons: Python loops vs NumPy.


01 - Array Math (NumPy)
================================

Purpose & mapping to the codebase
- Focus: implement the exact array-based pieces that replace per-particle Python/C++ work in `Atom.generateParticles` and `Atom.sphericalToCartesian` in `src/programs/Atom3D/main.py`.
- Outcomes: you will be able to create and update large particle sets (N≥100k) using NumPy without Python loops.

Goals (specific)
- Implement a `ParticleArrays` API that holds `r, theta, phi` and `x,y,z` as NumPy arrays.
- Replace any `for p in particles:` style loops with vectorized updates.

Core concepts (practical)
- `numpy.ndarray` shapes, dtype, and memory: store positions as `(N,3)` float32 for GL uploads.
- Broadcasting rules to apply a per-particle angular update (`phi += dphi`) without loops.
- Avoid repeated conversions: keep spherical coords if updates are angular-heavy; convert to Cartesian only when sending to GPU.

Plan (step-by-step)
1. Create `ParticleArrays` with fields: `r (N,)`, `theta (N,)`, `phi (N,)`, `pos (N,3)`.
2. Implement `spherical_to_cartesian(r,theta,phi)` returning shape `(N,3)` and `cartesian_to_spherical(pos)` returning `(r,theta,phi)`.
3. Implement `update_phi(phi, omega, dt)` where `omega` may be scalar or `(N,)` array; use `phi = (phi + omega*dt) % (2*pi)`.
4. Replace per-particle code in `Atom.generateParticles` with `ParticleArrays` usage and store `pos` as `np.float32` for the renderer.

Verification (concrete checks)
1. Roundtrip: random `r,theta,phi` -> `pos` -> `r2,theta2,phi2`. Assert these hold within tolerances:
	 - `max(abs(r-r2)) < 1e-9`
	 - `max(abs(((phi-phi2+np.pi)%(2*np.pi))-np.pi)) < 1e-9`
2. Performance: for `N=100_000`, time one `update_phi` and one `spherical_to_cartesian`; vectorized times should be much faster than Python loop.

Detailed Walkthrough (beginner-friendly)
1) File and API
Create `src/programs/Atom3D/mini_projects/01-array_math/impl.py` with these functions:
	- `create_particle_arrays(N)` -> returns dict with zeroed arrays
	- `spherical_to_cartesian(r, theta, phi)`
	- `cartesian_to_spherical(pos)`
	- `update_phi(phi, dphi)`

2) Implement `spherical_to_cartesian`
Use elementwise NumPy ops. Template:

```python
import numpy as np

def spherical_to_cartesian(r, theta, phi):
		x = r * np.sin(theta) * np.cos(phi)
		y = r * np.cos(theta)
		z = r * np.sin(theta) * np.sin(phi)
		return np.stack((x, y, z), axis=-1).astype(np.float32)
```

3) Implement `cartesian_to_spherical`
Compute `r = np.linalg.norm(pos, axis=1)`; `theta = np.arccos(np.clip(pos[:,1]/(r+eps), -1, 1))`; `phi = np.arctan2(pos[:,2], pos[:,0])`.

4) Implement `update_phi`
Accept `phi` array and `dphi` (scalar or array). Use `phi = (phi + dphi) % (2*np.pi)` to keep angles stable.

5) Integrate with `Atom.generateParticles`
Instead of creating a list of tuples, create arrays using above functions and store `self.particles_pos = pos` and `self.particles_color = colors`.
When drawing, upload `self.particles_pos` as a contiguous `np.float32` buffer to GL using `glBufferData` with `GL_DYNAMIC_DRAW`.

Notes & gotchas
- Use `np.float32` for GPU uploads to reduce memory and match GL expectations.
- Avoid creating Python lists for N>10k; keep everything in NumPy arrays.
