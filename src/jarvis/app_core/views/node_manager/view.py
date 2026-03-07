from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap


class ModuleOrganizerView(QWidget):
    def __init__(self, name, parent, settings):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        self.settings = settings

        self.bus_global = parent.bus
        self.bus = parent.bus.namespaced(name)

        self.mapping: dict[QLabel, QPixmap | None] = {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)