import mediapipe as mp

from jarvis.app_core import logger
from jarvis.app_core.threading import ThreadedResource


class HandTracker(ThreadedResource):
    def __init__(self, max_hands=2, detection_conf=0.6, tracking_conf=0.6):
        super().__init__()
        self.results = None
        try:
            self.mp_draw = mp.solutions.drawing_utils
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                max_num_hands=max_hands,
                min_detection_confidence=detection_conf,
                min_tracking_confidence=tracking_conf)
        except Exception as e:
            logger.info(f"Could not initialize hand tracking modules: {e}")
    
    def process_image(self, img):
        if img is None: return None
        self.results = self.hands.process(img)

    def overlay_tracking(self, img):
        if self.results is None or img is None: return img
        for lm in self.results.multi_hand_landmarks or []:
            self.mp_draw.draw_landmarks(img, lm, self.mp_hands.HAND_CONNECTIONS)
        return img
    
    def coordinates(self):
        if self.results.multi_hand_landmarks:
            print(self.results.multi_hand_landmarks)
        return False
