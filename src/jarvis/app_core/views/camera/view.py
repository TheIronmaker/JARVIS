from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

import numpy as np

from jarvis.utils.helpers.img import round_pixmap, get_frame
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
        # Later, create ability to create camera with special settings through pop-up-type interface.
        self.parent.bus.publish("create", {"type":"camera", "name":self.name})
    
    def stop_camera(self):
        self.parent.bus.publish("camera.destruct", True)
    
    def poll(self):
        links = self.settings.get("frame_links")
        frame = get_frame(links, self.bus_global)
        if frame is None: return
        
        height, width = frame.shape[:2]
        qt_image = QImage(frame.tobytes(), width, height, 3 * width, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.feed.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation)
        
        radius = self.settings.get("corner_radius", 0)
        self.feed.setPixmap(round_pixmap(pixmap, radius))
