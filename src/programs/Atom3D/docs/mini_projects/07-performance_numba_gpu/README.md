07 - Performance: Numba / GPU / Profiling
======================================

Goals
- Learn when to rely on NumPy, when to JIT with `numba`, and when to move work to GPU.
- Learn profiling tools to identify hotspots.

Core concepts
- `numba.njit` and parallel loops
- Using `cProfile`, `line_profiler`, and `timeit`
- GPU options: `moderngl` compute shaders, CUDA/pycuda (optional)

Plan
1. Profile the CPU update loop for N=250k and identify hotspots.
2. Try `numba`-accelerated version of the update function and measure speedup.
3. If still slow, prototype a compute-shader that updates phi on GPU and measure end-to-end.

Verification
- Numba speedup factor X (document measured numbers). Expect >3x for hotspot loops.
- If compute shader used, profile GPU sync time and compare full-frame time.
