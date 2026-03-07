from PySide6.QtWidgets import QWidget

class AtomSimView(QWidget):
    def __init__(self, name, parent, settings):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        self.settings = settings
        
        self.bus_global = parent.bus
        self.bus = parent.bus.namespaced(name)