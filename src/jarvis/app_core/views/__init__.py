from .view_manager import ViewManager

from .camera import CameraView
from .face_tracker.view import FaceTrackerView
from .hand_tracker.view import HandTrackerView
from .node_manager.view import ModuleOrganizerView
from .PCA9685 import PCA9685View, ServoUpdaterView

__all__ = {
    "camera": CameraView,
    "face_tracker": FaceTrackerView,
    "hand_tracker": HandTrackerView,
    "node_manager": ModuleOrganizerView,
    "PCA9685": PCA9685View,
    "servo_updater": ServoUpdaterView
}