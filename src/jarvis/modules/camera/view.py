from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QSizePolicy, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

from jarvis.modules.image_processing import *
from jarvis.settings import settings

class CameraView(QWidget):
    def __init__(self, parent=None):
        self.settings = settings["camera"]
        super().__init__(parent)
        self.parent = parent

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.feed = QLabel("No feed")
        self.feed.setAlignment(Qt.AlignCenter)
        self.feed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.feed.setStyleSheet(self.feed.setStyleSheet("QLabel {border-radius: " + str(self.settings["window_radius"]) + "px; background-color: black;}"))

        self.buttons = {"New Feed":QPushButton("Launch Camera Window")}
        self.buttons["New Feed"].clicked.connect(self.launch_camera)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(2)

        for _, button in self.buttons.items():
            btn_layout.addWidget(button, alignment=Qt.AlignHCenter)

        layout.addWidget(self.feed)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update(self, frame):
        if frame is None: return False
        print(frame)
        qt_image = QImage(frame.data, *frame.shape[:2], frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaledToWidth(self.feed.width(), Qt.FastTransformation)
        self.feed.setPixmap(round_pixmap(pixmap, 12))
        return True
    
    def launch_camera(self):
        self.parent.state["camera"]["show_output"] = True
        print("Starting Camera")