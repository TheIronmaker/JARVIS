import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QDockWidget, QSizePolicy
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt, QTimer

from jarvis.core.logger import Logger
from jarvis.app_core.views import ViewManager
from jarvis.utils.services.json_processor import load_json

BUILDS_PATH = Path(__file__).parent / "app_builds"

class MainWindow(QMainWindow):
    def __init__(self, bus):
        super().__init__()
        self.bus = bus

        self.build = load_json("app_build", BUILDS_PATH)
        self.view_managers = {}
        self.docks = {}

        self.load_view_managers()
        self._build_central()
    
    def load_view_managers(self):
        for manager in self.build.get("view_managers", []):
            if manager.get("enabled", True):
                name = manager.get("name")
                if not name:
                    Logger.error("View manager build missing name. Skipping.")
                    continue
                self.view_managers[name] = ViewManager(self, self.bus, name)

    def _build_central(self):
        self.setWindowTitle("JARVIS")
        self.setDockOptions(QMainWindow.AllowTabbedDocks)
        central = QWidget()
        layout = QHBoxLayout() # Will need config driven approach

        # Main area
        self.workspace = QLabel("Main workspace")
        self.workspace.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Will need to add layout configurations and more complex stacking options through config files
        for view_manager in self.view_managers.values():
            view_stack = view_manager.stack()
            if view_stack:
                #view_stack.addWidget(self.workspace)
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
    
    def paintEvent(self, event):
        # Handles all paint events. PySide6 painter may only be used within this function
        with QPainter(self) as painter:
            for view_manager in self.view_managers.values():
                view_manager.paint_views(event, painter)

def app(*args):
    app = QApplication(sys.argv)
    window = MainWindow(*args)
    window.resize(1200, 800)
    window.show()

    timer = QTimer()
    timer.setInterval(10)
    for view_manager in window.view_managers.values():
        timer.timeout.connect(view_manager.update)
    timer.start()

    app.exec()
