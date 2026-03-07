from logging import Logger
from pathlib import Path

from jarvis.core.threaded import ThreadedResource
from jarvis.core.databus import DataBus
from jarvis.modules import ModuleManager
from jarvis.app_core.app import app
from jarvis.utils.services.json_processor import load_json

CORE_BUILD_DIR = Path(__file__).parent
CORE_BUILDS_DIR = Path(__file__).parent / "core_builds"

class Core(ThreadedResource):
    def __init__(self, bus, name):
        self.bus = bus
        self.name = name
        self.settings = load_json(name, CORE_BUILDS_DIR)
        super().__init__(self.settings["cycle_time"])

        self.module_manager = ModuleManager(bus)
        self.module_manager.start_modules()

    def load_module_managers(self):
        for manager in self.build.get("module_managers", []):
            if manager.get("enabled", True):
                name = manager.get("name")
                if not name:
                    Logger.error("View manager build missing name. Skipping.")
                    continue

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
    build = load_json("core_build", CORE_BUILD_DIR)
    cores = {}
    for core_build in build.get("instances", []):
        name = core_build.get("name")
        core = Core(DataBus(), name)
        if core_build.get("enabled", True):
            if core_build.get("start_thread", True):
                core.start_thread()
            if core_build.get("run_method") == "app":
                app(core.bus, core.module_manager.build)
            cores[core.name] = core
    
    # Stops main program after application closes - needs to track running cores and close them properly
    for core in cores.values():
        core.module_manager.destruct()
        core.stop_thread()

if __name__ == "__main__":
    main()