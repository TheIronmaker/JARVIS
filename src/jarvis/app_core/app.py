from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QDockWidget, QSizePolicy
from PySide6.QtCore import Qt, QTimer
import sys

from jarvis.app_core.view_manager import ViewManager

class MainWindow(QMainWindow):
    def __init__(self, bus, build):
        super().__init__()
        self.bus = bus
        self.build = build
        self.docks = {}

        self.view_manager = ViewManager(self, bus)
        self._build_central()

        if self.build.get("private_tests"):
            from jarvis.private_tests.finance.view import FinanceWindow
            self.add_dock("finance", FinanceWindow(), dock_area="right")

    def _build_central(self):
        self.setWindowTitle("JARVIS")
        self.setDockOptions(QMainWindow.AllowTabbedDocks)
        central = QWidget()
        layout = QVBoxLayout()

        # Main area
        self.workspace = QLabel("Main workspace")
        self.workspace.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.workspace)

        view_stack = self.view_manager.stack()
        if view_stack:
            layout.addLayout(view_stack)

        # Finishing
        central.setLayout(layout)
        self.setCentralWidget(central)

    def add_dock(self, name, widget, dock_area="right", initial_size=300):
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
        self.docks[name] = dock

def app(*args):
    app = QApplication(sys.argv)
    window = MainWindow(*args)
    window.resize(1200, 800)
    window.show()

    timer = QTimer()
    timer.setInterval(10)
    timer.timeout.connect(window.view_manager.update)
    timer.start()

    app.exec()
