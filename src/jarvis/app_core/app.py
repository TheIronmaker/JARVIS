from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QDockWidget
)
from PySide6.QtCore import Qt, QTimer
import sys

from jarvis.modules.camera.view import CameraView

class MainWindow(QMainWindow):
    def __init__(self, shared_state):
        super().__init__()
        self.shared_state = shared_state
        self.setWindowTitle("JARVIS")
        self.setDockOptions(QMainWindow.AllowTabbedDocks)
        self.modules = {}

        self._build_central()

        from jarvis.private_tests.finance.view import FinanceWindow
        from jarvis.modules.hand_tracker.view import HandTrackerWindow

        self.add_module("finance", FinanceWindow(), dock_area="right")
        self.add_module("hand tracker", HandTrackerWindow(), dock_area="left")

    def _build_central(self):
        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Main workspace"))
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.camera_view = CameraView()
        layout.addWidget(self.camera_view)

    def add_module(self, name, widget, dock_area="right", initial_size=300):
        area = {
            "left": Qt.LeftDockWidgetArea,
            "right": Qt.RightDockWidgetArea,
            "top": Qt.TopDockWidgetArea,
            "bottom": Qt.BottomDockWidgetArea,
        }.get(dock_area, Qt.RightDockWidgetArea)

        dock = QDockWidget(name.capitalize(), self)
        dock.setWidget(widget)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.addDockWidget(area, dock)

        orientation = Qt.Horizontal if dock_area in ("left", "right") else Qt.Vertical
        self.resizeDocks([dock], [initial_size], orientation)
        self.modules[name] = dock
    
    def update_views(self):
        self.camera_view.update_frame(self.shared_state.get("camera_display"))

def run_app(shared_state):
    app = QApplication(sys.argv)
    window = MainWindow(shared_state)
    window.resize(1200, 800)
    window.show()

    timer = QTimer()
    timer.setInterval(33)
    timer.timeout.connect(window.update_views)
    timer.start()

    sys.exit(app.exec())
