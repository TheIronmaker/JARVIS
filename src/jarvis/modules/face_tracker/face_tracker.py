import mediapipe as mp

from jarvis.core.logger import Logger
from jarvis.core.threaded import ThreadedResource


class FaceTracker():    
    def __init__(self, name, bus, settings, max_faces=1, detection_conf=0.6, tracking_conf=0.6):
        self.bus_global = bus
        self.bus = bus.namespaced(name)
        self.settings = settings

        try:
            self.mp_draw = mp.solutions.drawing_utils
            self.face_connections = mp.solutions.face_mesh_connections.FACEMESH_TESSELATION
            self.faces = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=max_faces,
                refine_landmarks=True,
                min_detection_confidence=detection_conf,
                min_tracking_confidence=tracking_conf)
        except Exception as e:
            Logger.info(f"Could not initialize hand tracking modules: {e}")
        
        self.results = None
    
    def loop(self):
        while self.running:
            pass
    
    def process_image(self, img):
        if img is None: return None
        self.results = self.faces.process(img)

    def overlay_tracking(self, img):
        if self.results is None or img is None: return img
        for lm in self.results.multi_face_landmarks or []:
            self.mp_draw.draw_landmarks(img, lm, self.face_connections)
        return img
