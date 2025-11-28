import time
import cv2
import numpy as np

from jarvis.app_core import logger
from jarvis.app_core.threading.thread import ThreadedResource
from jarvis.settings import settings

class Camera(ThreadedResource):
    def __init__(self):
        self.settings = settings["Camera"]
        super().__init__(sleep_time=self.settings["CPU_time_limit"])
        self.img = 100 * np.ones((480, 640, 3), dtype=np.uint8)
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

    def img_rgb(self): return cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)

    def show_image(self):
        if self.img is None:
            logger.warning("Image Viewer active with no image to show")
        else:
            try:
                cv2.imshow("Camera Viewer", self.img)
            except Exception as e:
                logger.error(f"Unable to display image capture: {e}")
                return False
        return True

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()

cam = Camera()
cam.start()

try:
    while True:
        cam.show_image()
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    cam.stop()