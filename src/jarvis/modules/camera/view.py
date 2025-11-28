from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QSizePolicy, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt
import cv2

from jarvis.modules.camera import start_instance
from jarvis.settings import settings

class CameraView(QWidget):
    def __init__(self, parent=None):
        self.settings = settings["Camera"]
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.feed = QLabel("No feed")
        self.feed.setAlignment(Qt.AlignCenter)
        self.feed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.feed.setStyleSheet("""
        QLabel {
            border-radius: 12px;
            background-color: black;
            }
        """)

        self.buttons = {"new window":QPushButton("Launch Camera Window")}
        self.buttons["new window"].clicked.connect(self.launch_camera)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(2)

        for _, button in self.buttons.items():
            btn_layout.addWidget(button, alignment=Qt.AlignHCenter)

        layout.addWidget(self.feed)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_frame(self, frame, radius=None):
        if frame is None: return

        if radius is None:
            h, w, ch = frame.shape
            qt_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.feed.setPixmap(pixmap.scaled(
                self.feed.width(),
                self.feed.height(), 
                Qt.KeepAspectRatio, 
                Qt.FastTransformation))
            return True

        h, w, _ = frame.shape
        target_w, target_h = self.feed.width(), self.feed.height()
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)

        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        qt_image = QImage(resized.data, new_w, new_h, resized.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        rounded = QPixmap(target_w, target_h)
        rounded.fill(Qt.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, target_w, target_h, radius, radius)
        painter.setClipPath(path)

        x = (target_w - new_w) // 2
        y = (target_h - new_h) // 2
        painter.drawPixmap(x, y, pixmap)
        painter.end()

        self.feed.setPixmap(rounded)
    
    def launch_camera(self):
        start_instance()