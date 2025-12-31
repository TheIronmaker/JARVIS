from PySide6.QtWidgets import QWidget

from jarvis.settings import settings

class ModuleViewer:
    def __init__(self, parent, name="module_viewer"):
        super().__init__(parent)
        self.parent = parent
        self.name = name
        self.bus = parent.bus.namespaced(name)
        self.settings = settings["module_manager_view"]