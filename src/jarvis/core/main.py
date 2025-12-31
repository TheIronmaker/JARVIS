from time import sleep

from jarvis.settings import settings
from jarvis.core.threaded import ThreadedResource
from jarvis.core.databus import DataBus
from jarvis.core.module_manager import ModuleManager
from jarvis.modules.image_processing import *
from jarvis.app_core.app import app

class Core(ThreadedResource):
    def __init__(self, bus):
        self.bus = bus
        self.settings = settings.load("core", ["settings"])
        super().__init__(self.settings["cycle_time"])

        self.modules = ModuleManager(bus)
        self.modules.load_modules()

    def loop(self):
        while self.running:

            if self.bus.get("camera.create"):
                self.modules.create("camera")
                self.modules.start_module("camera")
                self.bus.publish("camera.create", False)

            if self.bus.get("camera.destruct", False) and self.modules.exists("camera"):
                self.modules.destruct("camera")
                self.bus.publish("camera.destruct", False)
 
            self.cycle_sleep()
    
    def close(self):
        self.modules.stop_mod()

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

def main():
    bus = DataBus()
    core = Core(bus)
    core.start_thread()
    core.modules.start_modules()

    if core.settings.get("run_method") == "app":
        app(bus)
    
    # Stops main program after application closes. Can be left out to keep main thread running.
    core.stop_thread()

if __name__ == "__main__":
    main()
