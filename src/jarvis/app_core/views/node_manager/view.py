from PySide6.QtWidgets import QWidget

from jarvis.core.logger import Logger

class ModuleViewer:
    def __init__(self, parent, settings):
        if not isinstance(settings, dict) or not settings:
            return False
        super().__init__(parent)
        self.parent = parent
        self.settings = settings
        self.name = settings.get("name")
        self.bus = parent.bus.namespaced(self.name)
        self.settings = settings["module_manager_view"]