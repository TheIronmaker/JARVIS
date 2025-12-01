import mediapipe as mp
import numpy as np

from jarvis.app_core import logger
from jarvis.app_core.threading import ThreadedResource


class HandTracker(ThreadedResource):
    def __init__(self, draw=True, max_hands=2, detection_conf=0.7, tracking_conf=0.7):
        super().__init__()
        self.draw = draw
        self.results = None
        self.img = None

        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                max_num_hands=max_hands,
                min_detection_confidence=detection_conf,
                min_tracking_confidence=tracking_conf
                )
            self.mp_draw = mp.solutions.drawing_utils
        
        except Exception as e:
            logger.info(f"Could not initialize hand tracking modules: {e}")
    
    def process_image(self, img):
        if img is None:
            logger.error("Image processor called with no image to process")
            return False
        self.results = self.hands.process(img)
        self.img = img

    def overlay_tracking(self):
        if self.results is not None and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(self.img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return self.img


"""
hand_tracker = HandTracker()

while True:
    hand_tracker.process_image()
    hand_tracker.overlay_tracking()

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break
"""