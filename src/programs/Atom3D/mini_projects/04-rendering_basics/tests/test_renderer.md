Renderer tests (manual)
=======================

This file lists manual/automated checks to validate rendering correctness.

Checks:
- Startup: window/context is created without errors.
- Buffer upload: positions and colors upload succeed (no GL errors).
- Draw: one frame renders points visible on screen.

Automated tests can assert that shader compilation returns no errors and that buffer sizes match expected.
