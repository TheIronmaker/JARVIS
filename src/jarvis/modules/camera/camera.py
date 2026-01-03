import cv2
import numpy as np
from time import sleep

from jarvis.core.logger import Logger
from jarvis.core.threaded import ThreadedResource

class Camera(ThreadedResource):    
    def __init__(self, bus, name, settings):
        super().__init__(settings.get("cycle_time"))
        self.bus = bus.namespaced(name)
        self.settings = settings

        self.blank = 100 * np.ones((480, 640, 3), dtype=np.uint8)
        self.img = self.blank.copy()

        try: self.cap = cv2.VideoCapture(0)
        except: Logger.error("Could not open camera")
    
    def loop(self):
        while self.running:
            self.capture_image()
            self.bus.publish("frame", self.img)
            
            self.cycle_sleep()
    
    def close(self):
        self.bus.publish("frame", None)
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()
    
    def capture_image(self, y_flip=True, color_flip=True):
        success, img = self.cap.read()
        if not success:
            Logger.error("Unable to capture video input")
            return False
        
        img = cv2.flip(img, 1) if y_flip else img
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if color_flip else img
        return self.img

    def show_output(self, img=None): # To be completely changed | It's a separate process camera viewer
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

    # NOT FINISHED
    def on_key_press(self, key):
        if key == "ESC":
            if cv2.waitKey(1) & 0xFF == 27:
                self.stop_thread()