from pathlib import Path

from jarvis.core.threaded import ThreadedResource
from jarvis.core.databus import DataBus
from jarvis.managers.module_manager import ModuleManager
from jarvis.app_core.app import app
from jarvis.utils.services.json_processor import load_json

CORE_DIR = Path(__file__).parent

class Core(ThreadedResource):
    def __init__(self, bus):
        self.bus = bus
        self.settings = load_json("settings", CORE_DIR)
        super().__init__(self.settings["cycle_time"])

        self.module_manager = ModuleManager(bus)
        self.module_manager.start_modules()

    def loop(self):
        while self.running:

            if self.bus.get("camera.create"):
                camera = self.module_manager.construct({"type":"camera", "name":"camera"}, [self.bus])
                if not isinstance(camera, str):
                    camera.start_thread()
                self.bus.publish("camera.create", False)

            if self.bus.get("camera.destruct", False) and self.module_manager.exists("camera"):
                self.module_manager.destruct("camera")
                self.bus.publish("camera.destruct", False)
 
            self.cycle_sleep()
    
    def close(self):
        self.module_manager.stop_mod()

def main():
    bus = DataBus()
    core = Core(bus)
    core.start_thread()

    if core.settings.get("run_method") == "app":
        app(bus, core.module_manager.build)
    
    # Stops main program after application closes. Can be left out to keep main thread running.
    core.module_manager.destruct()
    core.stop_thread()

if __name__ == "__main__":
    main()
