import time
import cv2
import numpy as np

from jarvis.app_core import logger
from jarvis.app_core.threading import ThreadedResource
from jarvis.settings import settings

class Camera(ThreadedResource):
    def __init__(self):
        self.settings = settings["Camera"]
        super().__init__(sleep_time=self.settings["CPU_time_limit"])
        self.blank = 100 * np.ones((480, 640, 3), dtype=np.uint8)
        self.img = self.blank.copy()
        try: self.cap = cv2.VideoCapture(0)
        except: logger.error("Could not open camera")
    
    def _loop(self):
        while self.running:
            self.capture_image()
            time.sleep(self.settings["CPU_time_limit"])
    
    def capture_image(self, flip=True):
        success, img = self.cap.read()
        if not success:
            logger.error("Unable to capture video input")
            return False
        if flip: self.img = cv2.flip(img, 1)
        else: self.img = img
        return True

    def img_rgb(self):
        if self.img is not None: return cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        return self.blank

    def show_output(self, img=None):
        display_img = img or self.img
        if display_img is None:
            logger.warning("Image Viewer active with no camera to show")
            return False
        try:
            cv2.imshow("Camera Viewer", display_img)
            return True
        except Exception as e:
            logger.error(f"Unable to display image: {e}")
            return False

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()