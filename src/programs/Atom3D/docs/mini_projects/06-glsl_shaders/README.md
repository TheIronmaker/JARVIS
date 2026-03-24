06 - GLSL Shaders Deep Dive
================================

Goals
- Learn GLSL vertex/fragment shader structure and how to port lighting/color calculations from C++ shader code.

Core concepts
- Varyings, uniforms, attribute inputs
- Lighting models (Lambertian, simple rim/glow), precision and varying interpolants
- Debugging shaders: compile logs and minimal test scenes

Plan
1. Translate the C++ vertex/fragment shaders to GLSL strings usable by `moderngl`.
2. Implement a shader that uses per-instance color and a simple rim/glow based on vertex normal.
3. Add toggles (uniforms) to change glow exponent and ambient intensity.

Verification
- Shader compiles with no errors; uniform updates produce visible changes; glow exponent visually tightens the highlight.
