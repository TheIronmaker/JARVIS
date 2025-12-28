from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

from jarvis.app_core.gui_elements import DisplaySlider

class HandTrackerView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

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
    
    def update(self):
        self.update_frame(self.readout, self.parent.bus.get("hand_tracker.coordinates_overlay"))
        self.update_frame(self.rotation_coor, self.parent.bus.get("hand_tracker.palm_gizmo"))
        self.slider.set_value(self.parent.bus.get("hand_tracker.slider_value", 0))

    def update_frame(self, label: QLabel, frame):
        if frame is None or label not in self.mapping: return
        self.mapping[label] = self._frame_to_pixmap(frame)
        self.rescale()