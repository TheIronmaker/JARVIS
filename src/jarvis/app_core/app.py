from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QDockWidget, QGroupBox, QSizePolicy
from PySide6.QtCore import Qt, QTimer
import sys

from jarvis.core.logger import Logger
from jarvis.modules.camera.view import CameraView
from jarvis.modules.hand_tracker.view import HandTrackerView

class ViewManager:
    def __init__(self, parent, bus, build):
        self.parent = parent
        self.bus = bus
        self.build = build
        self.defaults = {}
        self.views = {}
        self.classes = {
            "camera": CameraView,
            "hand_tracker":HandTrackerView
            }

    def load_views(self):
        for module in self.build.get("instances", []):
            self.load_view(module.get("settings", {}))
        
    def load_view(self, module):
        try:
            if module.get("view"):
                view_settings = module["view"]

                name = module.get("name")
                if not name:
                    Logger.error(f"Could not start view: Missing view name")
                    return None

                package = [self.parent]
                if view_settings:
                    package.append(view_settings)

                instance = self.classes[name](*package)
                self.views[name] = instance

        except Exception as e:
            Logger.error(f"Could not load view: {e}")
    
    def update(self):
        for name, view in self.views.items():
            try:
                view.update()
            except Exception as e:
                Logger.warning(f"Unable to update {name} view: {e}")

class MainWindow(QMainWindow):
    def __init__(self, bus, build):
        super().__init__()
        self.bus = bus
        self.build = build
        self.modules = {}
        self.view_manager = ViewManager(self, bus, build)
        self.view_manager.load_views()
        
        #self.camera_view = CameraView(self, {})
        #self.camera_box = self.create_view(self.camera_view, min_size=(125, 125))

        self._build_central()

        if self.build.get("private_tests"):
            from jarvis.private_tests.finance.view import FinanceWindow
            self.add_dock("finance", FinanceWindow(), dock_area="right")
        
        #self.hand_tracker_view = HandTrackerView(self)
        #self.add_dock("hand tracker", self.hand_tracker_view, dock_area="left", initial_size=500)

    def _build_central(self):
        self.setWindowTitle("JARVIS")
        self.setDockOptions(QMainWindow.AllowTabbedDocks)
        central = QWidget()
        layout = QVBoxLayout()

        # Main area

        self.workspace = QLabel("Main workspace")
        self.workspace.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.workspace)

        for view in self.view_manager.views.values():
            view_box = self.create_view(view)
            layout.addWidget(view_box)

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
        self.modules[name] = dock
    
    def create_view(self, view, min_size=(125, 125), max_size=(1000, 1000)):
        view_box = QGroupBox()
        view_box.setMinimumSize(min_size[0], min_size[1])
        view_box.setMaximumSize(max_size[0], max_size[1])

        layout = QVBoxLayout()
        layout.addWidget(view)
        layout.setContentsMargins(0, 0, 0, 0)
        view_box.setLayout(layout)

        return view_box

    def update_views(self):
        #self.camera_view.update(self.bus.get("hand_tracker.frame"))
        self.hand_tracker_view.update()

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
