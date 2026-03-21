03 - Spherical Coordinates & Transforms
======================================

Purpose & mapping to the codebase
- Focus: replace the small but error-prone parts in `Atom.sphericalToCartesian`, `generateParticles` and the per-particle current update in the C++ code that computes `theta`/`phi` and updates `phi`.

Goals (specific)
- Provide robust, vectorized `cartesian_to_spherical(pos)` and `spherical_to_cartesian(r,theta,phi)` functions.
- Provide helper `safe_acos` and a stable `wrap_angle` utility. Show how to use them in `Atom.generateParticles`.

Core concepts (practical)
- Use `np.clip` to keep inputs to `arccos` in [-1,1].
- Use `np.linalg.norm` with `axis=1` and small epsilon to avoid divide-by-zero.
- Use `np.arctan2` for phi to retain quadrant information.

Plan (step-by-step)
1. Implement `safe_acos(x)` which returns `np.arccos(np.clip(x, -1.0, 1.0))`.
2. Implement `cartesian_to_spherical(pos)`:
	 - `r = np.linalg.norm(pos, axis=1)`
	 - `theta = safe_acos(pos[:,1] / (r + eps))`
	 - `phi = np.arctan2(pos[:,2], pos[:,0])`
3. Implement `spherical_to_cartesian` as in the Array Math walkthrough.
4. Add `wrap_angle(phi)` that maps any angle to `(-pi, pi]` using `((phi+pi) % (2*pi)) - pi`.

Verification (concrete checks)
- Roundtrip: `pos -> (r,theta,phi) -> pos2`; assert `max(|pos-pos2|) < 1e-8` for random test sets excluding r≈0.
- Pole tests: create points with theta near 0 or pi and verify `phi` remains finite and updates don't produce NaNs.

Detailed Walkthrough (beginner-friendly)
1) File and API
- Create `src/programs/Atom3D/mini_projects/03-spherical_transforms/impl.py` with:
	- `safe_acos(x)`
	- `wrap_angle(phi)`
	- `cartesian_to_spherical(pos, eps=1e-12)`
	- `spherical_to_cartesian(r, theta, phi)`

2) Implement and test `safe_acos`
```python
import numpy as np

def safe_acos(x):
		return np.arccos(np.clip(x, -1.0, 1.0))
```

3) Implement `cartesian_to_spherical`
```python
def cartesian_to_spherical(pos, eps=1e-12):
		r = np.linalg.norm(pos, axis=1)
		theta = safe_acos(pos[:,1] / (r + eps))
		phi = np.arctan2(pos[:,2], pos[:,0])
		return r, theta, phi
```

4) Implement `wrap_angle` and use it after updates to keep angles numerically well-behaved.

5) How to integrate into `Atom.generateParticles`
- Use `cartesian_to_spherical` to recompute `r,theta,phi` after sampling or after applying angular updates.
- When computing velocities from the quantum current, produce `dphi` (angular velocity) and call `phi = wrap_angle(phi + dphi*dt)`.

Notes & gotchas
- Avoid computing `theta` / `phi` for `r==0`. Treat origin as a special case (set theta=0, phi=0) if needed.
- Use consistent dtype (`float64` for math, downcast to `float32` for GL upload).
