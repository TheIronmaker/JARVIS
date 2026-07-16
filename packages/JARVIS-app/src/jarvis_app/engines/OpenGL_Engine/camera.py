import math
import numpy as np

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication

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

                # Hiding cursor and saving position
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