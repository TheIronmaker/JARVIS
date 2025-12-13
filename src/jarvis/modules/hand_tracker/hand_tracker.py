import mediapipe as mp
import numpy as np
from importlib import resources
import json

from jarvis.app_core import logger
from jarvis.app_core.threading import ThreadedResource
from jarvis.modules.image_processor import *

class HandTracker(ThreadedResource):
    def __init__(self, max_hands=2, detection_conf=0.6, tracking_conf=0.6, shape=(1080, 1920)):
        super().__init__()
        try:
            self.mp_draw = mp.solutions.drawing_utils
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                max_num_hands=max_hands,
                min_detection_confidence=detection_conf,
                min_tracking_confidence=tracking_conf)
        except Exception as e:
            logger.info(f"Could not initialize hand tracking modules: {e}")
        
        self.shape = shape
        self.results = None
        self.Global, self.Local = np.zeros((21, 3)), np.zeros((21, 3))
        self.data = self.load_file(name="coordinate_base.json")
    
    def load_file(self, path="jarvis.modules.hand_tracker", name=""):
        with resources.open_text(path, name) as file:
            return json.load(file)

    def process_image(self, img):
        if img is None: return None
        self.results = self.hands.process(img)

    def overlay_tracking(self, img):
        if self.results is None or img is None: return img
        for lm in self.results.multi_hand_landmarks or []:
            self.mp_draw.draw_landmarks(img, lm, self.mp_hands.HAND_CONNECTIONS)
        return img
    
    def angle_3pts(self, a, b, c):
        ba = a - b
        bc = c - b
        cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    def get_coordinates(self):
        """ Retrieves Global and Local Coordinates """
        if self.results.multi_hand_landmarks:
            for _, hand in enumerate(self.results.multi_hand_landmarks):
                # Global Coordinates Array
                self.Global = np.array([[p.x, p.y, p.z] for p in hand.landmark])
                # Local Coordinates: Wrist Origin
                self.Local = self.Global - self.Global[0]

    def calculate_rotation(self):
        # Average of main points into plane/direction
        pass
        #points = np.array([[p.x, p.y, p.z] for i, p in enumerate(hand.landmark) if i in indices])

    def get_reading(self, version="Global"):
        if version == "Global": target = self.Global
        elif version == "Local": target = self.Local

        readout = []
        for p, (x, y, z) in enumerate(target):
            coords = [int(v * 100) for v in [x, y, z]]
            pads = [" " * abs(4 - len(str(c))) for c in coords]
            readout.append(f"X: {coords[0]},{pads[0]} Y: {coords[1]},{pads[1]} Z: {coords[2]},{pads[2]} | Point ID: {p}")
        
        return draw_text_list(readout, (1000, 1000), (20, 20))
