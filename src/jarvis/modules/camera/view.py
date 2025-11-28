from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt   

from jarvis.modules.camera import start_instance

class CameraView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel("No feed")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMaximumSize(640, 480)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        cam_btn = QPushButton("Launch Camera Window")
        cam_btn.clicked.connect(self.launch_camera)
        layout.addWidget(cam_btn)
    
    def update_frame(self, frame):
        if frame is None: return False
        h, w, ch = frame.shape
        Qframe = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(Qframe))
    
    def launch_camera(self):
        start_instance()