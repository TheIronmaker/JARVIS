import importlib
from pathlib import Path

from jarvis.core.logger import Logger
from jarvis.managers.node_manager import NodeManager
import jarvis.modules as modules
from jarvis.utils.services.path_resolver import PathResolver

MODULES_DIR = Path(__file__).parent

class ModuleManager(NodeManager):
    def __init__(self, bus, name):
        self.bus = bus
        self.name = name
        self.classes = modules.__all__

        # Create Manager Attributes
        super().__init__()
        self.initialize(self.classes, package=[bus])
        self.build = PathResolver.load_file("module_main", ".json", "project", "configs/managers/modules")
        self.load_structs(default_dir=("settings", MODULES_DIR))

    def start_modules(self):
        return [self.start_module(name) for name in self.nodes]

    def start_module(self, name):
        module = self.nodes.get(name)
        if module and "_start_thread" in dir(module) and callable(getattr(module,'_start_thread', None)):
            try:
                module._start_thread()
            except Exception:
                Logger.error(f"Unable to start thread for module: {name}")
            return True
        return False

    def stop_mod(self, name=None):
        if name is None:
            for module in self.nodes.values():
                if "_stop_thread" in dir(module) and callable(getattr(module,'_stop_thread', None)):
                    module._stop_thread()

        elif name in self.nodes:
            self.nodes[name]._stop_thread()

    # Move to node manager
    def destruct(self, name=None):
        try:
            self.stop_mod(name)
            if name:
                del self.nodes[name]
            if not self.exists(name):
                return True
        except Exception as e:
            message = " " + name if name else "s"
            Logger.error(f"Unable to properly destroy module{message}: {e}")
        return False

    def restart(self, name):
        self.destruct(name)
        self.create(name)
        return True

    def exists(self, name:str) -> bool:
        return True if name in self.nodes else False
    
    def access(self, name:str):
        return self.nodes.get(name, False)