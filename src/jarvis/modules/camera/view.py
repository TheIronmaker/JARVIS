from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QSizePolicy, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

from jarvis.modules.image_processing import *
from jarvis.core.data_services import *

class CameraView(QWidget):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.parent = parent
        self.settings = settings
        self.bus_global = parent.bus
        self.bus = parent.bus.namespaced("camera_view")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.feed = QLabel("No feed")
        self.feed.setAlignment(Qt.AlignCenter)
        self.feed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.feed.setStyleSheet(self.feed.setStyleSheet("QLabel {border-radius: " + str(self.settings.get("window_radius", 12)) + "px; background-color: black;}"))

        self.buttons = {"Start Camera": QPushButton("Start Camera"), "Stop Camera":QPushButton("Stop Camera")}
        self.buttons["Start Camera"].clicked.connect(self.start_camera)
        self.buttons["Stop Camera"].clicked.connect(self.stop_camera)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(2)

        for _, button in self.buttons.items():
            btn_layout.addWidget(button, alignment=Qt.AlignHCenter)

        layout.addWidget(self.feed)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def link_camera(self, link:str):
        if link and isinstance(link, str):
            self.settings["frame_link"] = link
    
    def unlink_camera(self):
        self.settings["frame_link"] = None
    
    def start_camera(self):
        self.parent.bus.publish("camera.create", True)
    
    def stop_camera(self):
        self.parent.bus.publish("camera.destruct", True)
    
    def update(self):
        link = self.settings.get("frame_link")
        if not link:
            return False
        
        frame = self.bus_global.get(link + ".frame")
        if frame is None or not hasattr(frame, "shape") or len(frame.shape) < 2:
            return False
        
        # Ensures frame is unbroken before updating - Threading issue
        frame = np.ascontiguousarray(frame)
        height, width = frame.shape[:2]
        qt_image = QImage(frame.tobytes(), width, height, 3 * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image.copy()).scaledToWidth(self.feed.width(), Qt.FastTransformation)

        self.feed.setPixmap(round_pixmap(pixmap, 12))
        return True