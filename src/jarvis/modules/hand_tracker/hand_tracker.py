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
        self.centroid, self.rotation_coor, self.rotation_vector = [np.zeros(3) for _ in range(3)]

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

    def get_coordinates(self):
        """ Retrieves Global and Local Coordinates """
        if self.results.multi_hand_landmarks:
            for _, hand in enumerate(self.results.multi_hand_landmarks):
                # Global Coordinates Array
                self.Global = np.array([[p.x, p.y, p.z] for p in hand.landmark])
                # Local Coordinates: Wrist Origin
                self.Local = self.Global - self.Global[0]

    def calculate_Cartesian(self):
        """ Calculates the palms center and rotation """

        # Average of main points into plane/direction
        points = self.Global[self.data["indices"]] # Retrieval of palm points
        if np.isnan(points).any(): return None
        self.centroid = points.mean(axis=0)        # Center point of hand

        p0, p1, p5, p17 = points
        
        v1 = p5-p1
        v2 = p17-p0

        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        if v1_norm != 0 and v2_norm != 0:
            v1 /= v1_norm
            v2 /= v2_norm

            v_avg = (v1 + v2) / 2.0
            y_axis = v_avg / np.linalg.norm(v_avg)

            coor = np.array([y_axis, [0, 0.0, 0.0], [0, 0.0, 0.0]])
            coor = np.nan_to_num(coor)

            return render_gizmo(coor, self.shape)
        return None
    
    def angle_3pts(self, a, b, c): # Finger angle
        ba = a - b
        bc = c - b
        cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    def get_reading(self, version="Global"):
        if version == "Global": target = self.Global
        elif version == "Local": target = self.Local

        readout = []
        for p, (x, y, z) in enumerate(target):
            coords = [int(v * 100) for v in [x, y, z]]
            pads = [" " * abs(4 - len(str(c))) for c in coords]
            readout.append(f"X: {coords[0]},{pads[0]} Y: {coords[1]},{pads[1]} Z: {coords[2]},{pads[2]} | Point ID: {p}")
        
        return draw_text_list(readout, (1000, 1000), (20, 20))
