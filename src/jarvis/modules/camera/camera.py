import cv2
import numpy as np
from time import sleep

from jarvis.modules.logger import Logger
from jarvis.settings import *
from jarvis.app_core.threading import ThreadedResource

class Camera(ThreadedResource):    
    def __init__(self):
        self.settings = settings["camera"]
        super().__init__(self.settings["cycle_time"])

        self.blank = 100 * np.ones((480, 640, 3), dtype=np.uint8)
        self.img = self.blank.copy()

        try: self.cap = cv2.VideoCapture(0)
        except: Logger.error("Could not open camera")
    
    def loop(self):
        while self.enabled:
            self.capture_image()

            if self.settings.get("show_output"):
                self.show_output(self.img)
            
            sleep(self.settings["cycle_time"])
        
        self.close()
    
    def capture_image(self, y_flip=True, color_flip=True):
        success, img = self.cap.read()
        if not success:
            Logger.error("Unable to capture video input")
            return False
        
        img = cv2.flip(img, 1) if y_flip else img
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if color_flip else img
        return self.img

    def show_output(self, img=None):
        display_img = img or self.img
        if display_img is None:
            Logger.warning("Image Viewer active with no camera to show")
            return False
        try:
            cv2.imshow("Camera Viewer", display_img)
            return True
        except Exception as e:
            Logger.error(f"Unable to display image: {e}")
            return False

    def on_key_press(self, key):
        if key == "ESC":
            if cv2.waitKey(1) & 0xFF == 27:
                self.close()

    def close(self):
        self.cap.release()
        #cv2.destroyAllWindows()