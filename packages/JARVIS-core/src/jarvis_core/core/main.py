from pathlib import Path

from jarvis_core.logger import Logger
from jarvis_core.threaded import ThreadedResource
from jarvis_core.databus import DataBus
from jarvis_core.modules import ModuleManager
from jarvis_app.app import app

from jarvis_core.utils.services.path_resolver import PathResolver

CONFIG = PathResolver.load_file("core_main", ".json", "project", "configs/core")
CORE_BUILD_DIR = Path(__file__).parent / "core_builds"

class Core(ThreadedResource):
    def __init__(self, id, parent_config=None):
        self.id = id
        self.parent_config = parent_config
        self.bus = DataBus()

        # Ideally, the id would be almost any type of data format a config could store.
        self.config = PathResolver.load_file(str(id), ".json", "project", "configs/core")
        super().__init__(self.config.get("cycle_time"))
    
        self.module_managers = {}
        self.load_module_managers()

    def initialize(self):
        if self.config.get("start_thread"):
            self._start_thread()
        
        if self.config.get("run_method") == "terminal":
            self.main_process()
        elif self.config.get("run_method") == "app":
            app(self.bus) # This will take over the main thread - Later create a method to handle this
            # First code will not end until all cores are stopped, right now.
            # Biggest issue: cores start in succession of each other, since the app takes over main thread

    def load_module_managers(self):
        for manager_build in self.config.get("module_managers", []):
            if manager_build.get("enabled", True):
                id = manager_build.get("id")
                if not id:
                    
                    Logger.error("Module manager build missing id. Skipping.")
                    continue
                manager = ModuleManager(self.bus, id)
                manager.start_modules()
                self.module_managers[id] = manager #@revisit-add: if id exists

    def _main_process(self):
        pass
    
    def _close(self):
        for module_manager in self.module_managers.values():
            module_manager.destruct()

def construct_cores(build):
    cores = {}
    for core_build in build.get("instances", []):
        id = core_build.get("id")
        if core_build.get("enabled") == False or not id:
            continue

        cores[id] = Core(id)
    return cores

# The Core factory is not refined now
def main():
    build = PathResolver.load_file("core_main", ".json", "project", "configs/core")
    cores = construct_cores(build)
    for core in cores.values():
        core.initialize()
    
    # Stops main program after application closes - needs to track running cores and close them properly
    for core in cores.values():
        for module_manager in core.module_managers.values():
            module_manager.destruct()
        core._stop_thread()

if __name__ == "__main__":
    main()