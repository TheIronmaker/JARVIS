import importlib
from pathlib import Path

from jarvis.core.logger import Logger
from jarvis.managers.node_manager import Manager
import jarvis.modules as modules

MODULE_MANAGER_DIR = Path(__file__).parent
MODULES_DIR = Path(__file__).parent.parent

class ModuleManager(Manager):
    def __init__(self, bus):
        self.bus = bus
        self.classes = modules.__all__

        # Create Manager Attributes
        super().__init__()
        self.initialize(self.classes, package=[bus])
        self.load_build(main_dir=("build", MODULE_MANAGER_DIR))
        self.load_structs(default_dir=(MODULES_DIR, "settings"))

    def start_modules(self):
        return [self.start_module(name) for name in self.nodes]

    def start_module(self, name):
        module = self.nodes.get(name)
        if module and "start_thread" in dir(module) and callable(getattr(module,'start_thread', None)):
            try:
                module.start_thread()
            except Exception:
                Logger.error(f"Unable to start thread for module: {name}")
            return True
        return False

    def stop_mod(self, name=None):
        if name is None:
            for module in self.nodes.values():
                if "stop_thread" in dir(module) and callable(getattr(module,'stop_thread', None)):
                    module.stop_thread()

        elif name in self.nodes:
            self.nodes[name].stop_thread()
    
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