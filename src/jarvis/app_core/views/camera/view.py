from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

import numpy as np

from jarvis.utils.helpers.img import round_pixmap
from jarvis.app_core.gui_elements import ButtonStack

class CameraView(QWidget):
    def __init__(self, name, parent, settings):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        self.settings = settings
        
        self.bus_global = parent.bus
        self.bus = parent.bus.namespaced(name)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.feed = QLabel("No feed")
        self.feed.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.feed.setAlignment(Qt.AlignCenter)
        # self.feed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.buttons = ButtonStack({"Start_Camera":self.start_camera, "Stop Camera":self.stop_camera})

        self.layout.addWidget(self.feed)
        self.layout.addLayout(self.buttons.layout)
        self.setLayout(self.layout)

    def add_link(self, link:str, placement=0):
        if link and isinstance(link, str):
            self.settings["frame_links"].insert(placement, link)
    
    def clear_links(self):
        self.settings["frame_links"] = []
    
    def start_camera(self):
        self.parent.bus.publish("camera.create", True)
    
    def stop_camera(self):
        self.parent.bus.publish("camera.destruct", True)
    
    def update(self):
        links = self.settings.get("frame_links")
        link = links[0] if links else None
        if not link:
            return False
        
        frame = self.bus_global.get(link + ".frame")
        if frame is None or not hasattr(frame, "shape") or len(frame.shape) < 2:
            return False
        
        # Ensures frame is unbroken before updating - Threading issue
        frame = np.ascontiguousarray(frame)
        height, width = frame.shape[:2]
        qt_image = QImage(frame.tobytes(), width, height, 3 * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image.copy()).scaled(self.feed.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.feed.setPixmap(round_pixmap(pixmap, self.settings.get("corner_radius")))
        return True