import cv2
import mediapipe as mp
import numpy as np

from jarvis.app_core import logger


class HandTracker:
    def __init__(self, draw=True, max_hands=2, detection_conf=0.7, tracking_conf=0.7):
        self.draw = draw
        self.results = None

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
    
    def process_image(self):
        if self.img is None:
            logger.error("Image processor called with no image to process")
            return False
        self.results = self.hands.process()
        return True

    def overlay_tracking(self):
        if self.results is not None and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(self.img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

hand_tracker = HandTracker()

while True:
    hand_tracker.capture_image()
    hand_tracker.process_image()
    hand_tracker.overlay_tracking()
    hand_tracker.show_image()

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break
