import mediapipe as mp

from jarvis.app_core import logger
from jarvis.app_core.threading import ThreadedResource


class FaceTracker(ThreadedResource):
    def __init__(self, max_faces=1, detection_conf=0.6, tracking_conf=0.6):
        super().__init__()
        self.results = None
        try:
            self.mp_draw = mp.solutions.drawing_utils
            self.face_connections = mp.solutions.face_mesh_connections.FACEMESH_TESSELATION
            self.faces = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=max_faces,
                refine_landmarks=True,
                min_detection_confidence=detection_conf,
                min_tracking_confidence=tracking_conf)
        
        except Exception as e:
            logger.info(f"Could not initialize hand tracking modules: {e}")
    
    def process_image(self, img):
        if img is None: return None
        self.results = self.faces.process(img)

    def overlay_tracking(self, img):
        if self.results is None or img is None: return img
        for lm in self.results.multi_face_landmarks or []:
            self.mp_draw.draw_landmarks(img, lm, self.face_connections)
        return img
