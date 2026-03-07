from PySide6.QtWidgets import QHBoxLayout, QGroupBox, QSizePolicy
from PySide6.QtGui import QPainter
from PySide6.QtCore import QTimer
from pathlib import Path

from jarvis.managers.node_manager import Manager
from jarvis.core.logger import Logger
from jarvis.app_core.views.camera.view import CameraView
from jarvis.app_core.views.hand_tracker.view import HandTrackerView
from jarvis.app_core.views.PCA9685 import PCA9685View, ServoUpdaterView

VIEW_MANAGER_DIR = Path(__file__).parent
VIEWS_DIR = Path(__file__).parent.parent.parent / "app_core" / "views"

class ViewManager(Manager):
    def __init__(self, parent, bus):
        # Load classes and build
        self.parent = parent
        self.bus = bus
        self.classes = {
            "camera": CameraView,
            "hand_tracker":HandTrackerView,
            "PCA9685":PCA9685View,
            "ServoUpdater":ServoUpdaterView
            }
        
        # Create Manager Attributes
        super().__init__()
        self.initialize(self.classes, main_dir=(VIEW_MANAGER_DIR, "build"), default_dir=(VIEWS_DIR, "settings"))
        self.load_structs(package=[parent])
        self.setup_view_timers()

    def create_view_box(self, view):
        layout = QHBoxLayout()
        layout.addWidget(view)

        view_box = QGroupBox()
        view_box.setLayout(layout)
        
        return view_box

    def stack(self, layout=None):
        if layout is None:
            layout = QHBoxLayout()

        for view in self.nodes.values():
            view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # For specific separation of container vs view
            container = None
            if hasattr(view, "settings") and view.settings.get("view_box"):
                container = self.create_view_box(view)
                view.container = container

            layout.addWidget(container or view)
        return layout
    
    def setup_view_timers(self):
        for name, view in self.nodes.items():
            try:
                settings = getattr(view, "settings", {})
                rate = settings.get("poll_ms")
                if rate:
                    timer = QTimer(self.parent)
                    timer.timeout.connect(lambda v=view: v.poll())
                    timer.start(int(rate))
                    view.timer = timer
            except Exception as e:
                Logger.warning(f"Unable to create timer for {name}: {e}")

    def paint_views(self, event, painter: QPainter=None):
        created = False
        if painter is None:
            painter = QPainter(self.parent)
            created = True

        for name, view in self.nodes.items():
            try:
                if hasattr(view, "paint"):
                    view.paint(event, painter)
            except Exception as e:
                Logger.warning(f"Unable to paint {name} view: {e}")
        
        if created:
            painter.end()

    def update(self):
        for name, view in self.nodes.items():
            try:
                if not hasattr(view, "timer"):
                    view.poll()
            except Exception as e:
                Logger.warning(f"Unable to update {name} view: {e}")