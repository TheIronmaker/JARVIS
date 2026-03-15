#!/usr/bin/env -S uv run --script

"""
A template for creating a PySide6 application with an OpenGL viewport using py-ngl.

This script sets up a basic window, initializes an OpenGL context, and provides
standard mouse and keyboard controls for interacting with a 3D scene (rotate, pan, zoom).
It is designed to be a starting point for more complex OpenGL applications.
"""

import ctypes
import sys
import traceback

import numpy as np
import OpenGL.GL as gl
from PySide6.QtCore import Qt
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGL import QOpenGLWindow
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow


VERTEX_SHADER = """#version 410 core
layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec3 inColour;

out vec3 vertColour;

void main()
{
    gl_Position = vec4(inPosition, 1.0);
    vertColour = inColour;
}"""

FRAGMENT_SHADER = """#version 410 core
precision highp float;

in vec3 vertColour;
out vec4 fragColour;

void main()
{fragColour = vec4(vertColour, 1.0);}
"""


VERTEX_DATA = np.array([
            -0.75, -0.75,0.0,1.0, 0.0, 0.0,  # Bottom-left vertex (red)
            0.0,  0.75,0.0, 0.0, 1.0,  0.0,  # Top vertex (green)
            0.75,  -0.75, 0.0, 0.0,  0.0, 1.0,  # Bottom-right vertex (blue)
            ],dtype=np.float32)


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

class OpenGLApple(QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.vertex_shader = VERTEX_SHADER
        self.fragment_shader = FRAGMENT_SHADER

        self.shader_id = None
        self.polygon_mode = gl.GL_FILL
    
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
        
        gl.glUseProgram(self.shader_id)
        
        # Cleanup by deleting shaders
        gl.glDeleteShader(vertex_id)
        gl.glDeleteShader(fragment_id)

    def resizeGL(self, w, h):
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

        # Set Draw modes
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, self.polygon_mode)

        # Clear the colour and depth buffers from the previous frame
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # The QWidget version of OpenGL for PySide6 does not keep all data in GPU.
        # Other programs may use the GPU, so we point back to the correct shader_id.
        if self.shader_id is not None:
            gl.glUseProgram(self.shader_id)
        else:
            raise RuntimeError("Shader program is not initialized. Cannot render without shaders.")

        # Bind arrays and draw
        gl.glBindVertexArray(self.triangle.vao_id)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

        gl.glBindVertexArray(0) # Unbind the vertex array after drawing
        gl.glUseProgram(0) # Unbind the shader program after drawing

        # Any glViewport or glClear calls should be made in paintGL to ensure they are applied every frame, especially after window resizing.

    def keyPressEvent(self, event) -> None:
        """
        Handles keyboard press events.

        Args:
            event: The QKeyEvent object containing information about the key press.
        """
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()

        elif key == Qt.Key_W:
            self.polygon_mode = gl.GL_LINE # Wireframe mode
        elif key == Qt.Key_S:
            self.polygon_mode = gl.GL_FILL # Solid fill mode
        
        elif key == Qt.Key_A:
            self.triangle._create_triangle(self.triangle.size + 0.1)
            #self.triangle.vertices[7:10] += 0.1
            #self.triangle._create_triangle(self.triangle.size)
        
        elif key == Qt.Key_D:
            self.triangle._create_triangle(self.triangle.size - 0.1)
            #self.triangle.vertices[7:10] -= 0.1
            #self.triangle._create_triangle(self.triangle.size)

        # Trigger a redraw to apply changes
        self.update()
        # Call the base class implementation for any unhandled events
        super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenGL Apple Test Suite")
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