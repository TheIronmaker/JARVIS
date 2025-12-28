import mediapipe as mp
import numpy as np
from time import sleep

from jarvis.settings import *
from jarvis.core.logger import Logger
from jarvis.core.threaded import ThreadedResource
from jarvis.modules import data_handler
from jarvis.modules.image_processing import *
from jarvis.modules.smooth_damp import SmoothDampArray

class HandTracker(ThreadedResource):
    """Handles hand tracking with sub-class Math for calculations.
    
    Args:
        max_hands: Max number of tracked hands
        detection_conf: Confidence in tracking
        shape: Acceptable formats: (width, height) or (width, height, depth)
               Depth is BGR
    """

    def __init__(self, bus, max_hands=2, detection_conf=0.6, tracking_conf=0.6, shape=(1080, 1920, 3), fov=12):
        self.settings = settings["hand_tracker"]
        super().__init__(self.settings["cycle_time"])
        self.bus = bus

        # Hand Tracking defaults and Objects
        try:
            self.mp_draw = mp.solutions.drawing_utils
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                max_num_hands=max_hands,
                min_detection_confidence=detection_conf,
                min_tracking_confidence=tracking_conf)
        except Exception as e:
            Logger.info(f"Could not initialize hand tracking modules: {e}")
        
        # Variables
        self.shape = shape if len(shape) == 3 else (*shape, 3)
        self.fov = fov
        self.img = np.zeros(self.shape, dtype=np.uint8)
        self.results = None
        self.array = np.zeros((21, 3))
        self.math = Math(self)
    
    def loop(self):
        while self.running:
            try:
                self.results = self.hands.process(self.img)
            except Exception as e:
                Logger.info(f"Could not process hand tracking: {e}")

            self.math.Global = self.get_coordinates()

            if self.settings["data_smoothing"]["enable"]:
                self.math.Global = self.math.SD.next(self.math.Global)
            
            self.math.calc_local()
            self.math.calc_cartesian()
            #print(self.math.centroid)

            self.cycle_sleep()

    def overlay_tracking(self, img):
        if self.results is None or img is None: return img
        for lm in self.results.multi_hand_landmarks or []:
            self.mp_draw.draw_landmarks(img, lm, self.mp_hands.HAND_CONNECTIONS)
        return img

    def get_coordinates(self):
        """ Retrieves Global and Local Coordinates """
        if self.results is None: return self.array
        if self.results.multi_hand_landmarks:
            for _, hand in enumerate(self.results.multi_hand_landmarks):
                self.array = np.array([[p.x, p.y, p.z] for p in hand.landmark])
        return self.array

class Math:
    def __init__(self, parent):
        self.parent = parent
        self.fov = parent.fov # or use parent.fov every time for the Math class and don't define as "self"
        self.shape = (21, 3)

        self.config = data_handler.load_json(path="jarvis.modules.hand_tracker", name="coordinate_base.json")

        self.Global, self.Local = parent.array, parent.array
        if self.parent.settings.get("data_smoothing", {}).get("enable"):
            self.SD = SmoothDampArray(self.shape)
            self.SD.update_defaults(*self.parent.settings.get("data_smoothing", {}).get("defaults"))

        self.centroid, self.rotation_coor, self.normal_palm = [np.zeros(3) for _ in range(3)]

    def calc_local(self):
        self.Local = self.Global - self.Global[0]

    def calc_cartesian(self):
        """ Calculates the palms center and rotation """

        # Average of main points into plane/direction
        points = self.Global[self.config["indices"]]
        if np.isnan(points).any(): return None
        self.centroid = points.mean(axis=0)

        a, b, c, d = points
        
        ab = a-b
        cd = c-d

        ab_norm = np.linalg.norm(ab)
        cd_norm = np.linalg.norm(cd)
        if ab_norm != 0 and cd_norm != 0:
            ab /= ab_norm
            cd /= cd_norm

            v_avg = (ab + cd) / 2.0
            y_axis = v_avg / np.linalg.norm(v_avg)

            # Needs to tell which side is up
            self.normal_palm = np.nan_to_num(y_axis)
    
    def angle_3pts(self, a, b, c): # Finger angle - maybe combine for palm vectors?
        ba = a - b
        bc = c - b
        cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    def readout(self, version=None):
        if version is None: return False
        if version == "Global": target = self.Global
        elif version == "Local": target = self.Local

        readout = []
        for p, (x, y, z) in enumerate(target):
            coords = [int(v) for v in [x, y, z]]
            pads = [" " * abs(4 - len(str(c))) for c in coords]
            readout.append(f"X: {coords[0]},{pads[0]} Y: {coords[1]},{pads[1]} Z: {coords[2]},{pads[2]} | Point ID: {p}")
        
        return draw_text_list(readout, (1000, 1000), (20, 20))
