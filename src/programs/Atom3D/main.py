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
import os
import sys
import atexit
import traceback
import numpy as np

# PySide6 imports
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow

# Local imports
from atom import Atom
from opengl_apple import OpenGLApple, set_QSurfaceFormat

try:
    from jarvis.core.databus import DataBus
    from jarvis.modules.camera.camera import CameraNode
    from jarvis.modules.hand_tracker.hand_tracker import HandTrackerNode

    bus = DataBus()
    camera = CameraNode("camera", bus, settings={"cycle_time": 0.015})
    camera._start_thread()

    tracker = HandTrackerNode("hand_tracker", bus, {
        "max_hands": 2,
        "detection_confidence": 0.5,
        "tracking_confidence": 0.5,
        "render_hands": False,
        "frame_links": ["camera"],
        "data_smoothing": {"enabled": True, "defaults": [10, 0.7, 0]}
    })
except:
    tracker = None
    camera = None

# Set the QSurfaceFormat before creating QApplication
set_QSurfaceFormat()

# N to equal 100000
config = {
    "orbital": {"n": 3, "l": 2, "m": 1, "N": 10000},
    "electron_r": 1.5
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atom Prob-Flow (Andy's python)")

        self.atom = Atom(config)
        self.atom.generateParticles()

        self.opengl_widget = OpenGLApple(self)
        self.setCentralWidget(self.opengl_widget)

        self.timer = QTimer(self, interval=6) # 16ms = ~60 FPS
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self):
        if tracker:
            data = tracker.math.data.get("global_SD")
            top = data[8] - data[4]
            elevation = np.arccos(-np.clip(top[1] / (np.linalg.norm(top) + 1e-6), -1.0, 1.0)) #+ np.pi / 2
            azimuth = -np.arctan2(top[2], top[0])
            scale = np.linalg.norm(data[8] - data[4])

            if elevation == 0: elevation = 0.001
            if azimuth == 0: azimuth = 0.001
            
            self.opengl_widget.camera.azimuth = azimuth
            self.opengl_widget.camera.elevation = elevation
            self.opengl_widget.camera.radius = 1/(scale if scale != 0 else 1) * 4

        self.opengl_widget.particles = self.atom.updateVelocities()
        self.opengl_widget.update()
        super().update()

    def close(self):
        self.timer.stop()
        super().close()

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
            if camera: camera._stop_thread()

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
            self.opengl_widget.camera.azimuth += 0.1
            update = False
        elif key == Qt.Key_M:
            self.opengl_widget.camera.azimuth -= 0.1
            update = False
        elif key == Qt.Key_B:
            self.opengl_widget.camera.elevation += 0.1
            update = False
        elif key == Qt.Key_V:
            self.opengl_widget.camera.elevation -= 0.1
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
            print(f"Quantum numbers updated: n={n}, l={l}, m={m}, N={N}")

        self.update()
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

    window = MainWindow(*args)
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec())

@atexit.register
def clear_terminal(message=None):
    if message is None:
        input("\nExiting Atom Simulator...\n\n(Press Enter to clear terminal)\n")
        os.system('cls' if os.name == 'nt' else 'clear\nclear')
        return
    
    if message or (len(sys.argv) > 1 and "--output" not in sys.argv):
        os.system('cls' if os.name == 'nt' else 'clear\nclear')
        print(message)

if __name__ == "__main__":
    clear_terminal(message="Starting Atom Simulator...")
    app()