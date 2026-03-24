02 - Probability Sampling & Special Functions
===========================================

Purpose & mapping to the codebase
- Focus: implement the samplers that correspond to `sampleR`, `sampleTheta`, and `samplePhi` in `src/programs/Atom3D/main.py`, and the radial/angular pieces used by `inferno_single`.

Goals (specific)
- Provide vectorized implementations of radial and angular samplers using `numpy` + `scipy.special`.
- Produce a reusable `RadialSampler` that builds a grid CDF and returns many samples cheaply via interpolation.

Core concepts (practical)
- Evaluate special functions (`eval_genlaguerre`, `lpmv`) over a grid and vectorize them for N-sample draws.
- Build a radial PDF on a grid r∈[0,rmax], accumulate to CDF, normalize, then use `numpy.interp` for sampling many u values.
- For theta: compute PDF ∝ sin(theta) * |P_l^m(cosθ)|^2, build its CDF on a theta grid and sample similarly.

Plan (step-by-step)
1. Implement `build_radial_cdf(n,l,rmax,Ngrid)` returning `r_grid` and `cdf` (both 1D arrays).
2. Implement `sample_r(cdf, r_grid, u_array)` as `np.interp(u_array, cdf, r_grid)` and return array of r samples.
3. Implement `build_theta_cdf(l,m,Ngrid)` computing `theta_grid` and normalized CDF of `sin(theta)*|P_l^m(cosθ)|^2`.
4. Implement `sample_theta` using the theta CDF and `np.interp`.
5. Use `np.random.random(size=N)` to create `u_array` and draw `r,theta,phi` arrays for `N` particles.

Verification (concrete checks)
1. Visual: histogram sampled `r` vs analytic radial PDF curve (plot or compute L2 distance); they should match closely for the given `n,l`.
2. Theta: histogram of `cos(theta)` weighted by sampling should match `|P_l^m(cosθ)|^2` shape.

Detailed Walkthrough (beginner-friendly)
1) File and API
- Create `src/programs/Atom3D/mini_projects/02-sampling_specialfuncs/impl.py` with:
	- `build_radial_cdf(n, l, rmax, Ngrid=4096)`
	- `sample_r_from_cdf(cdf, r_grid, size)`
	- `build_theta_cdf(l, m, Ngrid=2048)`
	- `sample_theta_from_cdf(theta_cdf, theta_grid, size)`

2) Build radial CDF (step-by-step)
- On a grid r_i, compute `rho = 2*r_i/(n*a0)`. Use `eval_genlaguerre(k, alpha, rho)` where `k=n-l-1`, `alpha=2*l+1`.
- Compute radial function R(r) = sqrt(norm) * exp(-rho/2) * rho**l * L_k^{alpha}(rho). Then PDF_r = r_i**2 * R(r_i)**2.
- Accumulate with `np.cumsum(pdf)` and normalize by final sum to get CDF.

3) Sample many r quickly
- Draw `u = np.random.random(size=N)`, then `r_samples = np.interp(u, cdf, r_grid)`.

4) Theta sampling
- Build `theta_grid` from 0..pi. For each theta compute x = cos(theta); `P = lpmv(m, l, x)` from `scipy.special.lpmv` (vectorized over x).
- `pdf_theta = np.sin(theta_grid) * P**2`. Build CDF via `np.cumsum`, normalize, and sample with `np.interp` as above.

5) Edge cases & numerical stability
- Clamp values passed to `lpmv` and `eval_genlaguerre` to valid ranges; watch factorial/gamma growth for large n (limit n for testing).
- Choose `rmax` = `10 * n**2 * a0` (heuristic from C++ code) to capture most radial mass.

Notes & gotchas
- Precompute CDFs per `(n,l,m)` combination and cache them to avoid rebuilding for each run.
- Use double precision when building CDFs (float64) and convert samples to float32 for rendering.
