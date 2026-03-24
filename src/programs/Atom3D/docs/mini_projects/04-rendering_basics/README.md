04 - Rendering Basics (moderngl / PyOpenGL)
==========================================

Goals
- Learn a Python OpenGL binding and render many points/particles efficiently.
- Understand VAO/VBO, attribute upload, and basic vertex/fragment shaders.

Core concepts
- Windowing (glfw/pyglet), context creation
- Buffer objects (VBO), VAO layout, attribute divisors
- Point sprites vs sphere meshes. Trade-offs for performance and quality.

Plan
1. Build a minimal window that renders a dynamic set of 3D points using `moderngl` or `PyOpenGL`.
2. Upload an N×3 float32 position buffer each frame and draw as `GL_POINTS` with a simple shader.
3. Replace per-vertex color with a per-instance color attribute.

Verification
- Render N=100k points at interactive framerate (>30 FPS) on modern hardware (or observe the bottleneck).
- Visual check that color attribute maps to particle colors.

Notes
- I recommend `moderngl` for concise API and compute-shader friendliness later.
