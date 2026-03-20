05 - Instancing & GPU Techniques
================================

Goals
- Learn instanced rendering, attribute divisors, and options for moving particle updates to GPU (transform feedback / compute shaders).

Core concepts
- `glDrawArraysInstanced` or equivalent in `moderngl`
- Per-instance attributes (position, color, scale)
- Transform feedback basics or compute shading to update positions on GPU

Plan
1. Convert the renderer to use a single sphere mesh and render many instances with per-instance position and color.
2. Measure CPU cost of uploading large buffers per-frame and explore double-buffering strategies.
3. (Optional) Implement a simple transform-feedback or compute-shader step to update phi on GPU.

Verification
- Rendering quality: instanced spheres align with CPU positions.
- Performance: compare frame times for direct buffer upload vs instanced draw with static buffers.
