03 - Spherical Coordinates & Transforms
======================================

Goals
- Build robust conversions between spherical and Cartesian coordinates for large arrays.
- Learn to handle degeneracies (sinθ ~ 0), stable atan2 usage, and angle wrapping.

Core concepts
- Vectorized `atan2`, `arccos`, `sin`, `cos` and safe guards for division by small numbers
- Choosing to store either Cartesian or spherical state based on update patterns

Plan
1. Implement vectorized cartesian_to_spherical and spherical_to_cartesian.
2. Implement numerically safe functions that clamp values to [-1,1] for `arccos`.
3. Implement a phi-update routine that updates only phi and leaves r/theta unchanged.

Verification
- Roundtrip conversions error < 1e-9 for random test inputs.
- Edge-case tests: points near poles, origin handling, negative zeros.
