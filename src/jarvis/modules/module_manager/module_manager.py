from pathlib import Path

from jarvis.core.logger import Logger
from jarvis.managers import Manager
from jarvis.utils.data_services import load_json
from jarvis.modules.camera import Camera
from jarvis.modules.hand_tracker import HandTracker
from jarvis.modules.face_tracker import FaceTracker

MODULE_MANAGER_DIR = Path(__file__).parent
MODULES_DIR = Path(__file__).parent.parent

class ModuleManager(Manager):
    def __init__(self, bus):
        self.bus = bus
        self.classes = {
            "camera": Camera,
            "hand_tracker": HandTracker,
            "face_tracker": FaceTracker
        }

        # Create Manager Attributes
        super().__init__()
        self.initialize(self.classes, main_dir=(MODULE_MANAGER_DIR, "build"), default_dir=(MODULES_DIR, "settings"))
        self.load_structs(package=[bus])
    
    # Move to Manager Class
    def create(self, type:str, name:str=None):
        name = name or type
        module_config = self.defaults.get(type)
        if not module_config:
            module_config = load_json(f"modules/{type}/settings", MODULES_DIR) or {}

            if not module_config:
                Logger.warning(f"Module settings inaccessible: {type}")
                module_config = {}
            
            self.defaults[type] = module_config
            self.build[name] = module_config
        
        self.load_module({"type":type, "name":name, "enabled":True, "settings":module_config}) # Could remove enabled setting

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
            return True

        elif name in self.nodes:
            self.nodes[name].stop_thread()
            return True
        
        return False
    
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