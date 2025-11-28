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
    
    def capture_image(self):
        success, self.img = self.cap.read()
        if not success:
            logger.error("Unable to capture video input")
            return False
        return True

    def img_rgb(self):
        if self.img is not None: return cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        return self.blank

    def show_output(self):
        if self.img is None:
            logger.warning("Image Viewer active with no image to show")
        else:
            try:
                cv2.imshow("Camera Viewer", self.img)
            except Exception as e:
                logger.error(f"Unable to display image capture: {e}")
                return False
        return True

    def show_frame(self, img):
        if self.img is None: logger.warning("Image Viewer active with no image to show")
        else:
            try:
                cv2.imshow("Camera Viewer", img)
            except Exception as e:
                logger.error(f"Unable to display image capture: {e}")
                return False
        return True

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()