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

# PySide6 imports
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow

# Local imports
from atom import Atom
from opengl_apple import OpenGLApple, set_QSurfaceFormat

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

        self.timer = QTimer(self, interval=16) # 16ms = ~60 FPS
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self):
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

        # Clamp orbital values to valid ranges
        if n < 1: n = 1
        if l > n - 1: l = n - 1
        if l < 0: l = 0
        if m > l: m = l
        if m < -l: m = -l
        if N <= 0: N = 10000

        electron_r = float(n) / 3.0
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
def clear_terminal(ask=None, message="Exiting Atom Simulator...\n\n(Press Enter to clear terminal)\n"):
    if (input(message) if ask is None else "") == "":
        os.system('cls' if os.name == 'nt' else 'clear\nclear')

if __name__ == "__main__":
    clear_terminal(ask=True, message="Starting Atom Simulator...")
    app()