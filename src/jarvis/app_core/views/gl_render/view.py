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
The OpenGL Rendering pipeline is ported to its python version.
"""

import math
import numpy as np

from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QCursor, QSurfaceFormat
from PySide6.QtWidgets import QApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import glm

from .shaders import VERTEX_SHADER, FRAGMENT_SHADER
from jarvis.modules.atom_sim import AtomSimNode

class PS6():
    @staticmethod
    def set_QSurfaceFormat():
        format = QSurfaceFormat()
        format.setSamples(4) # Request 4x multisampling for anti-aliasing
        format.setMajorVersion(4) # Request OpenGL version 4.1 as the highest supported version by macOS
        format.setMinorVersion(1)
        format.setProfile(QSurfaceFormat.CoreProfile) # Request a Core Profile context, which removes deprecated features
        format.setDepthBufferSize(24) # Request a 24-bit depth buffer for better z-depth precision

        # Set default format for all QSurface instances (QOpenGLWidget, QOpenGLWindow, etc.)
        QSurfaceFormat.setDefaultFormat(format) # Apply settings globally


class Camera():
    def __init__(self, parent):
        self.parent = parent
        self.target = np.array([0, 0, 0], dtype=np.float32)
        self.radius = 50
        self.azimuth = 0
        self.elevation = math.pi / 2
        self.orbit_speed = 0.01
        self.pan_speed = 0.01 #@Unused
        self.zoom_speed = 10

        self.dragging = False
        self.panning = False
        self.locked_pos = QPoint(0, 0)

        self.lastX, self.lastY = 0, 0

    def position(self):
        clamped_elevation = np.clip(self.elevation, 0.01, math.pi - 0.01)
        return np.array([
            self.radius * math.sin(clamped_elevation) * math.cos(self.azimuth),
            self.radius * math.cos(clamped_elevation),
            self.radius * math.sin(clamped_elevation) * math.sin(self.azimuth)
        ], dtype=np.float32)

    def update(self):
        self.target = np.zeros(3, dtype=np.float32)
    
    def process_mouse_move(self, event):
        x = event.position().x()
        y = event.position().y()

        dx = x - self.lastX
        dy = y - self.lastY
        if self.dragging:
            self.azimuth += dx * self.orbit_speed
            self.elevation -= dy * self.orbit_speed
            self.elevation = np.clip(self.elevation, 0.01, math.pi - 0.01)
        self.lastX = x
        self.lastY = y
        self.update()
    
    def process_mouse_button(self, event, action=None):
        button = event.button()
        if button in (Qt.LeftButton, Qt.MiddleButton):
            if action == "press":
                self.dragging = True

                # Hidding cursor and saving position
                self.lock_pos = QCursor.pos()
                self.parent.grabMouse()
                QApplication.setOverrideCursor(Qt.BlankCursor)
            else:
                self.dragging = False

                # Resetting Cursor position and revealing it
                QCursor.setPos(self.lock_pos)
                self.parent.releaseMouse()
                QApplication.restoreOverrideCursor()
    
    def process_scroll(self, event):
        self.radius -= event.angleDelta().y() * self.zoom_speed
        self.radius = max(0.1, self.radius)
        self.update()


class OpenGL_render(QOpenGLWidget):
    def __init__(self, name, parent, vertices:np.float32=None, particles:np.ndarray=None, scale=1.0):
        super().__init__()
        self.name = name
        self.parent = parent
        self.bus = parent.bus

        self.scale = scale
        self.particles = particles or np.array([], dtype=np.float32)

        self.setMouseTracking(True)
        self.vertices = vertices if vertices is not None else self.generate_sphere_vertices()
        self.vertex_shader = VERTEX_SHADER
        self.fragment_shader = FRAGMENT_SHADER

        self.modelLoc = None
        self.viewLoc = None
        self.projLoc = None
        self.colorLoc = None

        # OpenGL states (temp)
        self.shader_id = None
        self.polygon_mode = GL_FILL

        self.camera = Camera(self)

        config = [2,1,1,10000]
        self.atom = AtomSimNode(config)
        self.atom.generateParticles()

        self.timer = QTimer(self, interval=6) # 16ms = ~60 FPS
        self.timer.timeout.connect(self.poll)
        self.timer.start()

        self.bus.subscribe("hand_tracker.global_SD", self.hand_poll)
    
    def keyPressEvent(self, event) -> None:
        """
        Handles keyboard press events.

        Args:
            event: The QKeyEvent object containing information about the key press.
        """
        n, l, m, N, electron_r = self.atom.get_orbitals()
        update = True

        key = event.key()
        if key == Qt.Key_Escape:
            self.close()

        elif key == Qt.Key_W:
            n += 1
        elif key == Qt.Key_S:
            n -= 1
            if n < 1: n = 1
        elif key == Qt.Key_E:
            l += 1
        elif key == Qt.Key_D:
            l -= 1
            if l < 0: l = 0
        elif key == Qt.Key_R:
            m += 1
        elif key == Qt.Key_F:
            m -= 1
        elif key == Qt.Key_T:
            N += 10000
        elif key == Qt.Key_G:
            N -= 10000
        
        elif key == Qt.Key_N:
            self.camera.azimuth += 0.1
            update = False
        elif key == Qt.Key_M:
            self.camera.azimuth -= 0.1
            update = False
        elif key == Qt.Key_B:
            self.camera.elevation += 0.1
            update = False
        elif key == Qt.Key_V:
            self.camera.elevation -= 0.1
            update = False

        # Clamp orbital values to valid ranges
        if n < 1: n = 1
        if l > n - 1: l = n - 1
        if l < 0: l = 0
        if m > l: m = l
        if m < -l: m = -l
        if N <= 0: N = 10000

        electron_r = float(n) / 3.0
        if update:
            self.atom.set_orbitals(n, l, m, N, electron_r)

        self.poll()
        super().keyPressEvent(event)

    def close(self):
        self.timer.stop()
        super().close()

    def hand_poll(self, data):
        top = data[8] - data[4]
        elevation = np.arccos(-np.clip(top[1] / (np.linalg.norm(top) + 1e-6), -1.0, 1.0)) #+ np.pi / 2
        azimuth = np.arctan2(top[2], top[0])
        scale = np.linalg.norm(data[8] - data[4])

        if elevation == 0: elevation = 0.001
        if azimuth == 0: azimuth = 0.001
        
        self.camera.azimuth = azimuth
        self.camera.elevation = elevation
        self.camera.radius = 1/(scale if scale != 0 else 1) * 4

    def poll(self):
        self.particles = self.atom.updateVelocities()
        self.update()

    def mouseMoveEvent(self, event):
        self.camera.process_mouse_move(event)
        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        self.camera.process_mouse_button(event, "press")
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.camera.process_mouse_button(event, "release")
        return super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        self.camera.process_scroll(event)
        return super().wheelEvent(event)
    
    @staticmethod
    def sphericalToCartesian(r:np.ndarray, theta:np.ndarray, phi:np.ndarray) -> np.ndarray:
        return np.stack((
            r * np.sin(theta) * np.cos(phi),
            r * np.cos(theta),
            r * np.sin(theta) * np.sin(phi)),
            axis=-1).astype(np.float32)
    
    def generate_sphere_vertices(self, r=0.05, stacks=4, sectors=8) -> np.ndarray:
        phi = np.linspace(0, np.pi, stacks + 1)
        theta = np.linspace(0, 2 * np.pi, sectors + 1)
        phi, theta = np.meshgrid(phi, theta)
        grid = self.sphericalToCartesian(r, theta, phi)

        v1, v2, v3, v4 = grid[:-1, :-1], grid[1:, :-1], grid[1:, 1:], grid[:-1, 1:]
        return np.stack([v1, v2, v3, v1, v3, v4], axis=2).flatten()

    @staticmethod
    def check_shader_compilation_status(shader_id):
        if not glGetShaderiv(shader_id, GL_COMPILE_STATUS):
            e = glGetShaderInfoLog(shader_id)
            raise RuntimeError(f"Shader compilation failed: {shader_id}\n{e}")
    
    def initializeGL(self):
        # Make the OpenGL context current in this thread before calling any OpenGL functions
        self.makeCurrent()
        glEnable(GL_DEPTH_TEST) # Enable z-depth checking
        glEnable(GL_MULTISAMPLE) # Enable multisampling for anti-aliasing

        self.sphereVertexCount = len(self.vertices) // 3
        self.create_VBOVAO(self.vertices)

        # Create and compile vertex and fragment shaders
        vertexShader = glCreateShader(GL_VERTEX_SHADER) # Create vertex ID
        glShaderSource(vertexShader, self.vertex_shader) # Must set shader source before compiling
        glCompileShader(vertexShader)

        self.check_shader_compilation_status(vertexShader)
    
        fragmentShader = glCreateShader(GL_FRAGMENT_SHADER) # Create fragment ID
        glShaderSource(fragmentShader, self.fragment_shader) # Set shader source before compiling
        glCompileShader(fragmentShader)

        self.check_shader_compilation_status(fragmentShader)

        # Attach, link, and use shaders
        self.shaderProgram = glCreateProgram()
        glAttachShader(self.shaderProgram, vertexShader)
        glAttachShader(self.shaderProgram, fragmentShader)
        glLinkProgram(self.shaderProgram)

        # Retrieve uniform locations
        self.modelLoc = glGetUniformLocation(self.shaderProgram, "model")
        self.viewLoc = glGetUniformLocation(self.shaderProgram, "view")
        self.projLoc = glGetUniformLocation(self.shaderProgram, "projection")
        self.colorLoc = glGetUniformLocation(self.shaderProgram, "objectColor")

        # Deleting shaders after use prevents GPU memory leaks
        glDeleteShader(vertexShader)
        glDeleteShader(fragmentShader)

    def create_VBOVAO(self, vertices:np.float32, vertexCount=None):
        self.sphereVAO = glGenVertexArrays(1)
        self.sphereVBO = glGenBuffers(1)
        glBindVertexArray(self.sphereVAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.sphereVBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, None)
        glEnableVertexAttribArray(0)
        # Close the VAO so other instances don't break it
        glBindVertexArray(0)

    def destroy_VBOVAO(self, vao, vbo):
        """ Takes vao and vbo IDs and deletes them from OpenGL GPU memory.
        This prevents memory leaks when creating many new buffers. """
        glDeleteVertexArrays(1, [vao])
        glDeleteBuffers(1, [vbo])

    def paintGL(self): # drawSpheres
        """
        Main rendering loop called to redraw window. All drawing commands should be issued here.
        Any glViewport or glClear calls should be made in paintGL to ensure they are applied every frame, especially after window resizing.
        """
        self.makeCurrent()
        glClearColor(9/255, 14/255, 22/255, 1.0)

        # Match the viewport and window size to handle high-DPI displays correctly, mainly for MacOS
        ratio = self.devicePixelRatio()
        glViewport(0, 0, int(self.width() * ratio), int(self.height() * ratio))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shaderProgram)
        #glPolygonMode(GL_FRONT_AND_BACK, self.polygon_mode)

        # Set up transformation matrices (view, projection)
        projection = glm.perspective(glm.radians(45.0), self.width() / self.height() if self.height() > 0 else 1.0, 0.1, 2000.0)
        view = glm.lookAt(self.camera.position(), self.camera.target, np.array([0, 1, 0], dtype=np.float32))
        
        glUniformMatrix4fv(self.viewLoc, 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(self.projLoc, 1, GL_FALSE, glm.value_ptr(projection))

        glBindVertexArray(self.sphereVAO)

        try:
            for p in self.particles:
                # if p["pos"][0] < 0 and p["pos"][1] > 0: continue # Example of how to skip drawing certain areas
                model: glm.mat4 = glm.translate(glm.mat4(1.0), p["pos"])  # (N, 7) [:3] (x, y, z)
                model = glm.scale(model, glm.vec3(self.scale))
                glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, glm.value_ptr(model))
                glUniform4f(self.colorLoc, *p["color"]) # (N, 7) [3:7] (r, g, b, a)

                glDrawArrays(GL_TRIANGLES, 0, self.sphereVertexCount)
        except Exception as e:
            print(f"Error during drawing: {e}, line: {e.__traceback__.tb_lineno}")

        glBindVertexArray(0) # Unbind the vertex array after drawing
        glUseProgram(0) # Unbind the shader program after drawing
