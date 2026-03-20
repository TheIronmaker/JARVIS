02 - Probability Sampling & Special Functions
===========================================

Goals
- Learn how to implement radial and angular samplers for hydrogen-like orbitals in vectorized form.
- Use `scipy.special` for Associated Legendre and Generalized Laguerre functions.

Core concepts
- PDF -> CDF sampling at scale (precompute grids, use `numpy.interp`)
- `scipy.special.lpmv` and `scipy.special.eval_genlaguerre`
- Numerical stability and normalization of radial functions

Plan
1. Implement vectorized radial PDF and precompute CDF on a dense grid.
2. Implement theta sampling using Legendre polynomials (vectorized over many u samples).
3. Validate samplers by comparing histograms to analytic |psi|^2 shapes.

Verification
- For sample_R: histogram of r should match analytic radial distribution (chi-square visual check or KL divergence < threshold).
- For sample_theta: cos(theta) distribution should match expected P_l^m(cosθ) weighted by sinθ.
