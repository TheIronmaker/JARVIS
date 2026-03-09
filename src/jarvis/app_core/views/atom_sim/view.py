from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

class AtomSimView(QWidget):
    def __init__(self, name, parent):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        
        self.bus_global = parent.bus
        self.bus = parent.bus.namespaced(name)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.content_box = QLabel("AtomSim View")
        self.content_box.setStyleSheet("background-color: black; color: white;")
        self.content_box.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.content_box)

        self.setLayout(self.layout)