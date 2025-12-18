from time import sleep

from jarvis.app_core.threading import ThreadedResource
from jarvis.modules import Camera, HandTracker, FaceTracker
from jarvis.app_core.app import app

from jarvis.settings import settings
from jarvis.modules.image_processing import *

class Core(ThreadedResource):
    def __init__(self):
        self.settings = settings["main_frame"]
        super().__init__(self.settings["cycle_time"])

        self.modules = {
            "camera": Camera(),
            "hand_tracker": HandTracker(),
            "face_tracker": FaceTracker()
        }

        self.data = {name: {} for name in self.modules.keys()}

    def start_modules(self, name=None):
        if name is None:
            for name, module in self.modules.items():
                if settings[name].get("enabled"):
                    module.start()
        else:
            if name in self.modules and settings[name].get("enabled"):
                self.modules[name].start()
    
    def stop_modules(self, name=None):
        if name is None:
            for module in self.modules.values():
                module.stop()
        else:
            if name in self.modules:
                self.modules[name].stop()
    
    def loop(self):
        while self.settings["enabled"]:
            self.data["camera"]["feed"] = self.modules["camera"].img
            if self.data["camera"].get("show_output"):
                self.stop_modules("camera")

            sleep(self.settings["cycle_time"])
    
    def close(self):
        self.stop_modules()
        self.settings["enabled"] = False


# Deprecated function
def main_loop(modules, state):
    while True:
        frame = modules[0].img_rgb()
        modules[1].process_image(frame)
        modules[1].get_coordinates()
        modules[1].calculate_cartesian()

        coordinates_overlay = modules[1].get("Local")
        slider_value = modules[1].get("Normal", "Palm")

        palm_gizmo = render_gizmo(np.array([modules[1].normal_palm, [0, 0, 0], [0, 0, 0]]), modules[1].shape)

        state["camera"]["feed"] = modules[1].overlay_tracking(frame)
        state["hand_tracker"] = {"coordinates_overlay":coordinates_overlay, "palm_gizmo":palm_gizmo, "slider_value":slider_value[1]}



        # # Face Tracking
        # modules[2].process_image(frame)
        # state["camera_display"] = modules[2].overlay_tracking(frame)

        # # For status panel
        # state["status"]["cam_alive"] = cam.running
        # state["status"]["tracker_alive"] = tracker.running

        # Throttle update timing - to be refined
        sleep(0.01)

def main():
    core = Core()
    core.start()
    core.start_modules()

    if settings["main_frame"]["run_method"] == "app":
        app(core.data)
    
    core.close()

if __name__ == "__main__":
    main()
