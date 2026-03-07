from .view_manager import ViewManager

from .atom_sim import AtomSimView
from .camera import CameraView
from .face_tracker.view import FaceTrackerView
from .hand_tracker.view import HandTrackerView
from .node_manager.view import ModuleOrganizerView
from .PCA9685 import PCA9685View, ServoUpdaterView

__all__ = {
    "atom_sim": AtomSimView,
    "camera": CameraView,
    "face_tracker": FaceTrackerView,
    "hand_tracker": HandTrackerView,
    "node_manager": ModuleOrganizerView,
    "PCA9685": PCA9685View,
    "servo_updater": ServoUpdaterView
}