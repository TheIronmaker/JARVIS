from pathlib import Path

from jarvis.core.data_services import load_json
from jarvis.core.threaded import ThreadedResource
from jarvis.core.databus import DataBus
from jarvis.core.module_manager import ModuleManager
from jarvis.modules.image_processing import *
from jarvis.app_core.app import app

CORE_DIR = Path(__file__).parent

class Core(ThreadedResource):
    def __init__(self, bus):
        self.bus = bus
        self.settings = load_json("settings", CORE_DIR)
        super().__init__(self.settings["cycle_time"])

        self.module_manager = ModuleManager(bus)
        self.module_manager.load_modules()

    def loop(self):
        while self.running:

            if self.bus.get("camera.create"):
                self.module_manager.create("camera")
                self.module_manager.start_module("camera")
                self.bus.publish("camera.create", False)
                

            if self.bus.get("camera.destruct", False) and self.module_manager.exists("camera"):
                self.module_manager.destruct("camera")
                self.bus.publish("camera.destruct", False)
 
            self.cycle_sleep()
    
    def close(self):
        self.module_manager.stop_mod()

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
    core.module_manager.start_modules()

    if core.settings.get("run_method") == "app":
        app(bus, core.module_manager.build)
    
    # Stops main program after application closes. Can be left out to keep main thread running.
    core.module_manager.destruct()
    core.stop_thread()

if __name__ == "__main__":
    main()
