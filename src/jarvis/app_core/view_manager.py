import traceback
from pathlib import Path

from PySide6.QtWidgets import QHBoxLayout, QGroupBox, QSizePolicy
from PySide6.QtGui import QPainter
from PySide6.QtCore import QTimer

from jarvis.core.logger import Logger
from jarvis.managers.node_manager import NodeManager
import jarvis.app_core.views as app_views
from jarvis.utils.services.path_resolver import PathResolver

VIEWS_DIR = Path(__file__).parent / "views"

class ViewManager(NodeManager):
    def __init__(self, parent, bus, config):
        self.parent = parent
        self.bus = bus
        self.config = config
        self.classes = app_views.__all__
        
        # Create Manager Attributes - restrict this from running if GUI does not show it (dynammic loading of views as needed)
        super().__init__()
        self.initialize(self.classes, package=[parent])
        self.build = PathResolver.load_file(config["manager"], ".json", "project", "configs/managers/views")
        self.load_structs(default_dir=("settings", VIEWS_DIR))

        # Setup Views
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
                if not hasattr(view, "timer") and hasattr(view, "poll"):
                    view.poll()
            except Exception:
                Logger.warning(f"Unable to update {name} view. Full error: {traceback.format_exc()}")

    def keyPressEvent(self, event):
        for view in self.nodes.values():
            view.keyPressEvent(event)