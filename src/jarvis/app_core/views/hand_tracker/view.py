from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

import numpy as np

from jarvis.app_core.gui_elements import DisplaySlider
from jarvis.utils.helpers.img import get_frame

class HandTrackerView(QWidget):
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

        self.readout = self.add_feed()
        self.rotation_coor = self.add_feed()
        self.slider = DisplaySlider("Axis Rotation", value=40, min_val=-1, max_val=1)
        self.layout.addWidget(self.slider)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.rescale()

    def rescale(self):
        for label, map in self.mapping.items():
            if map: label.setPixmap(map.scaled(label.size(), Qt.KeepAspectRatio, Qt.FastTransformation))

    def add_feed(self) -> QLabel:
        label = QLabel(alignment=Qt.AlignTop | Qt.AlignHCenter)
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.layout.addWidget(label)
        self.mapping[label] = None
        return label

    @staticmethod
    def _frame_to_pixmap(frame): # Move to image_processing
        h, w, ch = frame.shape
        img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        return QPixmap.fromImage(img)
    
    def poll(self):
        links = self.settings.get("frame_links")
        self.update_frame(self.readout, get_frame(links, self.bus_global))
        #self.update_frame(self.rotation_coor, self.bus.get("palm_gizmo"))
        #self.slider.set_value(self.bus.get("slider_value", 0))

    def update_frame(self, label: QLabel, frame):
        if not frame or label not in self.mapping: return
        self.mapping[label] = self._frame_to_pixmap(frame)
        self.rescale()