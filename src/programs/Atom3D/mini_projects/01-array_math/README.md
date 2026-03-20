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

Verification
- Generate N=100k particles and measure time for one full update step; expect NumPy vectorized update < 1/10 of naive loop.
- Validate coordinate inversion: start from random `r,theta,phi` -> `x,y,z` -> back and assert max error < 1e-9.
