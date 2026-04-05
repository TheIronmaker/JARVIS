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
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow

# Local imports
from atom import Atom
from opengl_apple import OpenGLApple, set_QSurfaceFormat

# Set the QSurfaceFormat before creating QApplication
set_QSurfaceFormat()

# N to equal 100000
config = {
    "orbital": {"n": 4, "l": 2, "m": 0, "N": 10000},
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

        electron_r = float(atom.n) / 3.0

        self.update()
        # self.opengl_widget.update() #Maybe?
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
def clear_terminal(ask=None):
    if (input("Press Enter to clear terminal... ") if ask is None else "") == "":
        os.system('cls' if os.name == 'nt' else 'clear\nclear')

if __name__ == "__main__":
    clear_terminal(ask=True)
    app()