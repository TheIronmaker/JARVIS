from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QDockWidget
)
from PySide6.QtCore import Qt
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modular App")
        self.setDockOptions(QMainWindow.AllowTabbedDocks)
        self.modules = {}

        self._build_central()

        from private_tests.finance.view import FinanceWindow
        from modules.hand_tracker.view import HandTrackerWindow

        self.add_module("finance", FinanceWindow(), dock_area="right")
        self.add_module("hand tracker", HandTrackerWindow(), dock_area="left")

    def _build_central(self):
        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Main workspace"))
        central.setLayout(layout)
        self.setCentralWidget(central)

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

        # size hint
        orientation = Qt.Horizontal if dock_area in ("left", "right") else Qt.Vertical
        self.resizeDocks([dock], [initial_size], orientation)

        self.modules[name] = dock

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())
