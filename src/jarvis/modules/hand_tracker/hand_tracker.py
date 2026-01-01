import mediapipe as mp
import numpy as np

from jarvis.core.logger import Logger
from jarvis.modules import data_handler
from jarvis.modules.image_processing import *
from jarvis.modules.smooth_damp import SmoothDampArray

class HandTracker:
    """Handles hand tracking with sub-class Math for calculations.
    
    Args:
        name: 
        max_hands: Max number of tracked hands
        detection_conf: Confidence in tracking
        shape: Acceptable formats: (width, height) or (width, height, depth)
               Depth is BGR
    """

    def __init__(self, bus, settings, max_hands=2, detection_conf=0.6, tracking_conf=0.8, shape=(1080, 1920, 3), fov=12):
        self.bus_global = bus
        self.bus = bus.namespaced(settings.get("name"))
        self.settings = settings

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
        self.results = None
        self.array = np.zeros((21, 3))
        self.math = Math(self)

        # Subscribe Functions
        self.bus_global.subscribe("camera.frame", self.main_process)
    
    def main_process(self, frame):
        if frame is None: return False
        frame = frame.copy()

        self.process(frame)

        if self.settings["render_hands"]:
            self.bus.publish("frame", self.overlay_tracking(frame))
        
        self.math.data["global"] = self.get_coordinates()

        if self.settings["data_smoothing"]["enabled"]:
            self.math.SD.next(self.math.data["global"], update=True)
        
        self.math.calc_local()
        self.math.calc_cartesian()
        self.bus.publish("coordinates_overlay", self.math.readout("local"))
        self.bus.publish_many(self.math.data)

    def process(self, img):
        if img is None:
            self.results = None
            return
        try:
            self.results = self.hands.process(img) or self.results
        except Exception as e:
            Logger.info(f"Could not process image for hand tracking: {e}")

    def overlay_tracking(self, img):
        if self.results is None or img is None: return None
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

        self.data = {
            "global":np.zeros(self.shape),
            "local":np.zeros(self.shape),
            "centroid":np.zeros(3),
            "rotation_coor":np.zeros(3),
            "palm_normal":np.zeros(3)
        }

        if self.parent.settings.get("data_smoothing", {}).get("enabled"):
            self.SD = SmoothDampArray(self.shape)
            self.SD.update_defaults(*self.parent.settings.get("data_smoothing", {}).get("defaults"))

    def calc_local(self):
        self.data["local"] = self.data["global"] - self.data["global"][0]

    def calc_cartesian(self):
        """ Calculates the palms center and rotation """

        # Average of main points into plane/direction
        points = self.data["global"][self.config["indices"]]
        if np.isnan(points).any(): return None
        self.data["centroid"] = points.mean(axis=0)

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
            self.data["palm_normal"] = np.nan_to_num(y_axis)
    
    def angle_3pts(self, a, b, c): # Finger angle - maybe combine for palm vectors?
        ba = a - b
        bc = c - b
        cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    def readout(self, version:str=""):
        if version == "": return False

        readout = []
        for p, (x, y, z) in enumerate(self.data[version]):
            coords = [int(v) for v in [x, y, z]]
            pads = [" " * abs(4 - len(str(c))) for c in coords]
            readout.append(f"X: {coords[0]},{pads[0]} Y: {coords[1]},{pads[1]} Z: {coords[2]},{pads[2]} | Point ID: {p}")
        
        return draw_text_list(readout, (1000, 1000), (20, 20))
