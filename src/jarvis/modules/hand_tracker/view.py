from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt


class HandTrackerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.feed = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(self.feed)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def update_frame(self, frame):
        if frame is None: return
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        scaled = pixmap.scaled(
        self.feed.width(),
        self.feed.height(),
        Qt.KeepAspectRatio,
        Qt.FastTransformation)
        self.feed.setPixmap(scaled)
