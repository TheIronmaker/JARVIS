09 - Integration Harness
========================

Goals
- Bring together samplers, array math, camera, and renderer into a single, interactive demo.
- Provide a minimal test harness to verify each subsystem.

Core concepts
- Clear separation between `physics` (samplers, updates) and `render` (GL context, shaders)
- Small CLI to toggle subsystems for debugging

Plan
1. Provide a `run_demo.py` that wires together the other mini-project modules.
2. Add command-line flags: `--N`, `--n`, `--l`, `--m`, `--renderer`.
3. Add small unit/integration checks that can run headless (no GL) to validate samplers and transforms.

Verification
- Running `run_demo.py --help` prints available flags.
- Headless tests validate samplers and transforms; visual run shows interactive renderer.
