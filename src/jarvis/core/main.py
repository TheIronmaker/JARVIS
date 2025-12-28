from time import sleep

from jarvis.settings import settings
from jarvis.core.threaded import ThreadedResource
from jarvis.core.databus import DataBus
from jarvis.core.module_manager import ModuleManager
from jarvis.modules import Camera, HandTracker, FaceTracker
from jarvis.modules.image_processing import *
from jarvis.app_core.app import app

class Core(ThreadedResource):
    def __init__(self, bus):
        self.bus = bus
        self.settings = settings["main_frame"]
        super().__init__(self.settings["cycle_time"])

        self.modules = ModuleManager(bus)
        self.modules.bulk_create({
            "camera": Camera,
            "hand_tracker": HandTracker
        }) # Face Tracker

    def loop(self):
        while self.running:
            sleep(self.settings["cycle_time"])


    def OLDloop(self):
        while self.running:

            if self.modules.get("camera"):
                self.data["camera"]["feed"] = self.modules["camera"].img

            if self.data.get("camera") and self.data["camera"].get("stop_camera"):
                self.data["camera"]["stop_camera"] = False
                self.stop_modules("camera")

            if self.data.get("camera") and self.data["camera"].get("start_camera"):
                self.data["camera"]["start_camera"] = False

                self.modules["camera"] = Camera(self.bus)
                self.start_modules("camera")
            
            if self.modules.get("camera"):
                self.modules["hand_tracker"].img = self.modules["camera"].img
            
            sleep(self.settings["cycle_time"])
    
    def close(self):
        self.modules.stop()


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
    bus = DataBus()
    core = Core(bus)
    core.start()
    core.modules.start()

    if settings["main_frame"]["run_method"] == "app":
        app(bus)
    
    # Stops main program after application closes. Can be left out to keep main thread running.
    core.stop()

if __name__ == "__main__":
    main()
