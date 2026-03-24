Profiling instructions
----------------------

1. Run `python -m cProfile -o profile.out run_benchmark.py`
2. Use `snakeviz profile.out` or `gprof2dot` to inspect call graph.
3. Identify top functions and try `numba.njit` for those.
