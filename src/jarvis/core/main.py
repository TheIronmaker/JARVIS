from logging import Logger
from pathlib import Path

from jarvis.core.threaded import ThreadedResource
from jarvis.core.databus import DataBus
from jarvis.modules import ModuleManager
from jarvis.app_core.app import app
from jarvis.utils.services.json_processor import load_json

CORE_DIR = Path(__file__).parent
CORE_BUILD_DIR = Path(__file__).parent / "core_builds"

class Core(ThreadedResource):
    def __init__(self, bus, name):
        self.bus = bus
        self.name = name
        self.build = load_json(name, CORE_BUILD_DIR)
        super().__init__(self.build.get("cycle_time"))
    
        self.module_managers = {}
        self.load_module_managers()

    def load_module_managers(self):
        for manager_build in self.build.get("module_managers", []):
            if manager_build.get("enabled", True):
                name = manager_build.get("name")
                if not name:
                    Logger.error("Module manager build missing name. Skipping.")
                    continue
                manager = ModuleManager(self.bus, name)
                manager.start_modules()
                self.module_managers[name] = manager

    def main_process(self):
        pass
        """
        # Will need to make a dynamic module creation system: Thoughts:
        # module sends signal including which manager it came from, if module managed, so it can put it there.
        # Might also create option to include the name of a module to put it in, regardless of where it came from.
        if self.bus.get("camera.create"):
            camera = self.module_manager.construct({"type":"camera", "name":"camera"}, [self.bus])
            if not isinstance(camera, str):
                camera.start_thread()
            self.bus.publish("camera.create", False)

        if self.bus.get("camera.destruct", False) and self.module_manager.exists("camera"):
            self.module_manager.destruct("camera")
            self.bus.publish("camera.destruct", False)
        """
    
    def close(self):
        for module_manager in self.module_managers.values():
            module_manager.destruct()

def main():
    build = load_json("core_build", CORE_DIR)
    cores = {}
    for core_build in build.get("instances", []):
        name = core_build.get("name")
        if core_build.get("enabled") == False or not name:
            continue

        core = Core(DataBus(), name)
    
        if core_build.get("start_thread"):
            core.start_thread()
        
        if core_build.get("run_method") == "terminal":
            pass
        elif core_build.get("run_method") == "app":
            app(core.bus)
            # First code will not end until all cores are stopped, right now.
            # Biggest issue: cores start after each other, since app takes over main thread
        
        cores[name] = core
    
    # Stops main program after application closes - needs to track running cores and close them properly
    for core in cores.values():
        for module_manager in core.module_managers.values():
            module_manager.destruct()
        core.stop_thread()

if __name__ == "__main__":
    main()