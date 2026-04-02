#!/usr/bin/env -S uv run --script

"""
ATOM SIMULATOR PROGRAM - JARVIS
-------------------------------------------------
Description: A Python/OpenGL implementation of an interactive atom simulator.
Original Logic & C++ Implementation: Kavan (https://github.com)
YouTube Reference: https://www.youtube.com

Translated and adapted to Python by: Andy
Role: Sub-feature for JARVIS Assistant Project
-------------------------------------------------
Note: This module is a port of Kavan's 'Atoms' project. 
All scientific equations used are standard physics implementations.
"""

# System imports
import ctypes
import sys
import traceback
import numpy as np
import math

# PySide6 imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow

# OpenGL imports
import OpenGL.GL as gl
import glm

# Local imports
from atom import Atom
from shaders import VERTEX_SHADER, FRAGMENT_SHADER

# N to equal 100000
config = {
    "orbital": {"n": 4, "l": 2, "m": 0, "N": 10000},
    "electron_r": 1.5
}

def set_QSurfaceFormat():
    format: QSurfaceFormat = QSurfaceFormat()
    format.setSamples(4) # Request 4x multisampling for anti-aliasing
    format.setMajorVersion(4) # Request OpenGL version 4.1 as the highest supported version by macOS
    format.setMinorVersion(1)
    format.setProfile(QSurfaceFormat.CoreProfile) # Request a Core Profile context, which removes deprecated features
    format.setDepthBufferSize(24) # Request a 24-bit depth buffer for better z-depth precision

    # Set default format for all QSurface instances (QOpenGLWidget, QOpenGLWindow, etc.)
    QSurfaceFormat.setDefaultFormat(format) # Apply settings globally


class Triangle:
    def __init__(self, size):
        self.size = size
        self.vertices = np.array([
            -0.75, -0.75,0.0,1.0, 0.0, 0.0,
            0.0,  0.75,0.0, 0.0, 1.0,  0.0,
            0.75,  -0.75, 0.0, 0.0,  0.0, 1.0,
            ],dtype=np.float32)

        self._create_triangle(size)

    def change_size(self, size):
        self.size = size
        self._create_triangle(size)

    def _create_triangle(self, change:float=0):
        # Scale the vertex positions by the specified size
        self.vertices[0:3] = self.vertices[0:3] * change
        self.vertices[6:9] = self.vertices[6:9] * change
        self.vertices[12:15] = self.vertices[12:15] * change
        
        # fmt: off | on ?
        # allocate a VertexArray
        self.vao_id = gl.glGenVertexArrays(1)
        # now bind a vertex array object for our verts
        gl.glBindVertexArray(self.vao_id)

        vbo_id = gl.glGenBuffers(1)
        #  now bind this to the VBO buffer
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
        #  allocate the buffer data
        # Use .nbytes for numpy arrays to get the total byte size. OpenGL can sometimes struggle on MacOS with this.
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_STATIC_DRAW)
        #  now fix this to the attribute buffer 0
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, self.vertices.itemsize * 6, ctypes.c_void_p(0))
        #  enable and bind this attribute (will be inPosition in the shader)
        gl.glEnableVertexAttribArray(0)
        #  now fix this to the attribute buffer 0
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, self.vertices.itemsize * 6, ctypes.c_void_p(self.vertices.itemsize * 3))
        #  enable and bind this attribute (will be inPosition in the shader)
        gl.glEnableVertexAttribArray(1)
        gl.glBindVertexArray(0)

class Camera:
    def __init__(self):
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.radius = 50.0
        self.azimuth = 0.0
        self.elevation = math.pi / 2.0
        self.orbit_speed = 0.01
        self.pan_speed = 0.01
        self.zoom_speed = 0.1

        self.dragging = False
        self.panning = False

        self.lastX = 0.0
        self.lastY = 0.0
    
    def position(self):
        try:
            clamped_elevation = np.clip(self.elevation, 0.01, math.pi - 0.01)
            return np.array([
                self.radius * math.sin(clamped_elevation) * math.cos(self.azimuth),
                self.radius * math.cos(clamped_elevation),
                self.radius * math.sin(clamped_elevation) * math.sin(self.azimuth)],
                dtype=np.float32)
        except Exception as e:
            print(f"Error in position calculation: {e}")
            return np.array([0.0, 0.0, 0.0], dtype=np.float32)

    def update(self):
        self.target = np.identity(3, dtype=np.float32)

class OpenGLApple(QOpenGLWidget):
    class Engine:
        def __init__(self, parent):
            self.parent = parent
    
    def __init__(self, parent):
        super().__init__(parent)
        self.vertex_shader = VERTEX_SHADER
        self.fragment_shader = FRAGMENT_SHADER

        # Temp definitions
        self.sphereVAO = None
        self.sphereVBO = None
        self.sphereVertexCount = None

        self.modelLoc = None
        self.viewLoc = None
        self.projLoc = None
        self.colorLoc = None

        # OpenGL states (temp)
        self.shader_id = None
        self.polygon_mode = gl.GL_FILL

        self.camera = Camera()
        self.atom = Atom(config)
        self.atom.generateParticles()
    
    def create_VBOVAO(self, vertices:np.float32):
        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 12, None)
        gl.glEnableVertexAttribArray(0)
        gl.glBindVertexArray(0)

    def check_shader_compilation_status(self, shader_id):
        if not gl.glGetShaderiv(shader_id, gl.GL_COMPILE_STATUS):
            e = gl.glGetShaderInfoLog(shader_id)
            raise RuntimeError(f"Shader compilation failed: {shader_id}\n{e}")
    
    def initializeGL(self):
        # Make the OpenGL context current in this thread before calling any OpenGL functions
        self.makeCurrent()
        gl.glClearColor(9/255, 14/255, 22/255, 1.0) # Set the background color
        gl.glEnable(gl.GL_DEPTH_TEST) # Enable z-depth checking
        gl.glEnable(gl.GL_MULTISAMPLE) # Enable multisampling for anti-aliasing

        self.triangle = Triangle(1.0)
        self.load_shaders()

    def load_shaders(self, vertex_source: str = None, fragment_source: str = None):
        if vertex_source is not None:
            self.vertex_shader = vertex_source
        if fragment_source is not None:
            self.fragment_shader = fragment_source
        
        self.shader_id = gl.glCreateProgram()

        # Create and compile vertex and fragment shaders
        vertex_id = gl.glCreateShader(gl.GL_VERTEX_SHADER) # Create vertex ID
        gl.glShaderSource(vertex_id, self.vertex_shader) # Must set shader source before compiling
        gl.glCompileShader(vertex_id)
        self.check_shader_compilation_status(vertex_id)
    
        fragment_id = gl.glCreateShader(gl.GL_FRAGMENT_SHADER) # Create fragment ID
        gl.glShaderSource(fragment_id, self.fragment_shader) # Set shader source before compiling
        gl.glCompileShader(fragment_id)
        self.check_shader_compilation_status(fragment_id)

        # Attach, link, and use shaders
        gl.glAttachShader(self.shader_id, vertex_id)
        gl.glAttachShader(self.shader_id, fragment_id)
        gl.glLinkProgram(self.shader_id)

        # Retrieve uniform locations
        self.modelLoc = gl.glGetUniformLocation(self.shader_id, "model")
        self.viewLoc = gl.glGetUniformLocation(self.shader_id, "view")
        self.projLoc = gl.glGetUniformLocation(self.shader_id, "projection")
        self.colorLoc = gl.glGetUniformLocation(self.shader_id, "objectColor")

        print(f"\nUniform locations:\n"
              f"model = {self.modelLoc if self.modelLoc != -1 else 'Not found'}\n"
              f"view = {self.viewLoc if self.viewLoc != -1 else 'Not found'}\n"
              f"projection = {self.projLoc if self.projLoc != -1 else 'Not found'}\n"
              f"objectColor = {self.colorLoc if self.colorLoc != -1 else 'Not found'}")

        gl.glUseProgram(self.shader_id)
        
        # Cleanup by deleting shaders
        gl.glDeleteShader(vertex_id)
        gl.glDeleteShader(fragment_id)

    def resizeGL(self, w, h):
        # Might be able to remove ratio calculations from paintGL with this method
        ratio = self.devicePixelRatio()
        self.window_width = int(w * ratio)
        self.window_height = int(h * ratio)

    def paintGL(self):
        """
        Main rendering loop called to redraw window. All drawing commands should be issued here.
        """
        self.makeCurrent()

        # Match the viewport and window size to handle high-DPI displays correctly, mainly for MacOS
        ratio = self.devicePixelRatio()
        gl.glViewport(0, 0, int(self.width() * ratio), int(self.height() * ratio))
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, self.polygon_mode)

        # QOpenGLWidget on MacOS does not maintain OpenGL data across frames, so we need to re-bind our shader program and vertex arrays every time we draw.
        if self.shader_id is not None:
            gl.glUseProgram(self.shader_id)
        else:
            raise RuntimeError("Shader program is not initialized. Cannot render without shaders.")
        
        # Set up transformation matrices (view, projection)
        aspect = self.width() / self.height() if self.height() > 0 else 1.0
        projection = glm.perspective(glm.radians(45.0), aspect, 0.1, 100.0)
        view = glm.lookAt(self.camera.position(), self.camera.target, np.array([0, 1, 0], dtype=np.float32))

        
        gl.glUniformMatrix4fv(self.viewLoc, 1, gl.GL_FALSE, glm.value_ptr(view))
        gl.glUniformMatrix4fv(self.projLoc, 1, gl.GL_FALSE, glm.value_ptr(projection))

        #gl.glBindVertexArray(self.sphereVAO)

        # Much code for particles, then: gl.glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, glm.value_ptr(model))

        gl.glUniform4f(self.colorLoc, 1.0, 0.5, 0.31, 1.0)



        # Bind arrays and draw
        gl.glBindVertexArray(self.triangle.vao_id)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

        gl.glBindVertexArray(0) # Unbind the vertex array after drawing
        gl.glUseProgram(0) # Unbind the shader program after drawing

        # Any glViewport or glClear calls should be made in paintGL to ensure they are applied every frame, especially after window resizing.

    def drawSpheres(self, particles):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        if self.shader_id is not None:
            gl.glUseProgram(self.shader_id)
        else:
            raise RuntimeError("Shader program is not initialized. Cannot render without shaders.")
        
        # Set up transformation matrices (view, projection)
        aspect = self.width() / self.height() if self.height() > 0 else 1.0
        projection = glm.perspective(glm.radians(45.0), aspect, 0.1, 100.0)
        view = glm.lookAt(self.camera.position(), self.camera.target, np.array([0, 1, 0], dtype=np.float32))

        gl.glUniformMatrix4fv(self.viewLoc, 1, gl.GL_FALSE, glm.value_ptr(view))
        gl.glUniformMatrix4fv(self.projLoc, 1, gl.GL_FALSE, glm.value_ptr(projection))

        #gl.glBindVertexArray(self.sphereVAO)
        # Much code for particles, then: gl.glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, glm.value_ptr(model))
        for p in particles:
            if p.pos.x ==1:pass


    def keyPressEvent(self, event) -> None:
        """
        Handles keyboard press events.

        Args:
            event: The QKeyEvent object containing information about the key press.
        """

        atom = self.atom

        key = event.key()
        if key == Qt.Key_Escape:
            self.close()

        # Keybinds
        elif key == Qt.Key_W:
            atom.n += 1
            atom.generateParticles()
            
        elif key == Qt.Key_S:
            atom.n -= 1
            if atom.n < 1:
                atom.n = 1
            atom.generateParticles()

        elif key == Qt.Key_E:
            atom.l += 1
            atom.generateParticles()
        
        elif key == Qt.Key_D:
            atom.l -= 1
            if atom.l < 0:
                atom.l = 0
            atom.generateParticles()
        
        elif key == Qt.Key_R:
            atom.m += 1
            atom.generateParticles()
        
        elif key == Qt.Key_F:
            atom.m -= 1
            atom.generateParticles()
        
        elif key == Qt.Key_T:
            atom.N += 100000
            atom.generateParticles()
        
        elif key == Qt.Key_G:
            atom.N -= 100000
            atom.generateParticles()

        # Clamp orbital values to valid ranges
        if atom.l > atom.n - 1:
            atom.l = atom.n - 1
        if atom.l < 0:
            atom.l = 0
        if atom.m > atom.l:
            atom.m = atom.l
        if atom.m < -atom.l:
            atom.m = -atom.l

        electron_r = float(atom.n) / 3

        # Trigger a redraw to apply changes
        self.update()
        # Call the base class implementation for any unhandled events
        super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atom Prob-Flow (Andy's python)")
        self.opengl_widget = OpenGLApple(self)
        self.setCentralWidget(self.opengl_widget)
    
    def keyPressEvent(self, event):
        # Forward key events to the OpenGL widget for handling
        self.opengl_widget.keyPressEvent(event)
        super().keyPressEvent(event)

class DebugApplication(QApplication):
    """
    A custom QApplication subclass for improved debugging.

    By default, Qt's event loop can suppress exceptions that occur within event handlers
    (like paintGL or mouseMoveEvent), making it very difficult to debug as the application
    may simply crash or freeze without any error message. This class overrides the `notify`
    method to catch these exceptions, print a full traceback to the console, and then
    re-raise the exception to halt the program, making the error immediately visible.
    """

    def __init__(self, argv):
        super().__init__(argv)

    def notify(self, receiver, event):
        """
        Overrides the central event handler to catch and report exceptions.
        """
        try:
            # Attempt to process the event as usual
            return super().notify(receiver, event)
        except Exception:
            # If an exception occurs, print the full traceback
            traceback.print_exc()
            # Re-raise the exception to stop the application
            raise

def app(*args):
    if len(sys.argv) > 1 and "--debug" in sys.argv:
        app = DebugApplication(sys.argv)
    else:
        app = QApplication(sys.argv)

    set_QSurfaceFormat()

    window = MainWindow(*args)
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    app()