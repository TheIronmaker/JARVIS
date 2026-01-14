from pathlib import Path

from jarvis.managers import Manager
from jarvis.core.logger import Logger
from jarvis.app_core.views.camera.view import CameraView
from jarvis.app_core.views.hand_tracker.view import HandTrackerView

from jarvis.utils.data_services import load_json

VIEW_MANAGER_DIR = Path(__file__).parent
VIEWS_DIR = Path(__file__).parent.parent / "views"

class ViewManager(Manager):
    def __init__(self, parent, bus):
        self.parent = parent
        self.bus = bus
        self.classes = {
            "camera": CameraView,
            "hand_tracker":HandTrackerView
            }
        
        # Create Manager Attributes
        super().__init__()
        self.initialize(self.classes, main_dir=(VIEW_MANAGER_DIR, "build"), default_dir=(VIEWS_DIR, "settings"))
        self.load_structs(package=[parent])

    def update(self):
        for name, view in self.nodes.items():
            try:
                view.update()
            except Exception as e:
                Logger.warning(f"Unable to update {name} view: {e}")