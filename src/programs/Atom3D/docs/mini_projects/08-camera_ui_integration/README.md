08 - Camera, Interaction & Integration
=====================================

Goals
- Implement an orbit/pan/zoom camera and hook mouse/keyboard controls to the renderer.

Core concepts
- Camera spherical parameters: `radius`, `azimuth`, `elevation` and conversion to position
- Mouse callbacks for dragging, panning, scroll for zoom
- Decoupling camera math from rendering for testability

Plan
1. Implement a `Camera` class with `position()` and input handlers.
2. Integrate camera with renderer: build view matrix and pass as uniform.
3. Add keyboard shortcuts to change quantum numbers and regenerate samples.

Verification
- Camera orbit responds to mouse drag; zoom with scroll; panning modifies target.
- View matrix updates result in expected visual transforms.
