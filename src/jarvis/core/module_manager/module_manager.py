from pathlib import Path

from jarvis.settings import load_module_settings
from jarvis.core.logger import Logger
from jarvis.core.data_services import load_merged, load_json, merge_dictionary
from jarvis.modules import *

MODULE_MANAGER_DIR = Path(__file__).parent
MODULES_DIR = Path(__file__).parent.parent.parent

class ModuleManager:
    def __init__(self, bus):
        self.bus = bus
        self.build = load_json("build", MODULE_MANAGER_DIR)
        self.defaults = {}
        self.modules = {}
        self.classes = {
            "camera": Camera,
            "hand_tracker": HandTracker,
            "face_tracker": FaceTracker
        }

    def load_modules(self):
        """Loads all modules in the modules.json settings file and creates the modules"""
        for module in self.build.get("instances", []):
            self.load_module(module)
        return True

    def create(self, type:str, name:str=None):
        name = type if name is None else name
        module_config = self.defaults.get(type)
        if not module_config:
            module_config = load_json(f"modules/{type}/settings", MODULES_DIR) or {}

            if not module_config:
                Logger.warning(f"Module settings inaccessible: {type}")
                module_config = {}
            
            self.defaults[type] = module_config
            self.build[name] = module_config
        
        self.load_module({"type":type, "name":name, "enabled":True, "settings":module_config}) # Could remove enabled setting
        
    def load_module(self, module:dict):
        """Manages module settings and config quality before sending to init_module for class initialization"""
        if module.get("enabled", True) == False:
            return None

        mod_type = module.get("type")
        if not mod_type:
            Logger.error("Module Type not provided. Module failed to build")
            return False

        name = module.get("name") or module.get("type") or name
        if name is None:
            Logger.error(f"Module failed to build, insufficient name provided: {name}")
            return False
        
        if name in self.modules:
            Logger.error(f"Failed to start module with duplicate name: {name}")
            return False
        
        if name not in self.defaults:
            self.defaults[name] = load_json(f"modules/{name}/settings", MODULES_DIR)
        
        cls = self.classes.get(mod_type)
        if not cls:
            Logger.error(f"Module class does not exist: {mod_type}")
            return False

        package = [self.bus, name]
        settings = merge_dictionary(self.defaults.get(name), module.get("settings", {}))
        if settings:
            package.append(settings)

        self.init_module(name, cls, package)

    def init_module(self, name, cls, package):
        try:
            instance = cls(*package)
            self.modules[name] = instance
        except Exception as e:
            Logger.error(f"Unable to initialize {name} module: {e}")

    def start_modules(self):
        return [self.start_module(name) for name in self.modules]

    def start_module(self, name):
        module = self.modules.get(name)
        if module and "start_thread" in dir(module) and callable(getattr(module,'start_thread', None)):
            try:
                module.start_thread()
            except Exception:
                Logger.error(f"Unable to start thread for module: {name}")
            return True
        return False

    def stop_mod(self, name=None):
        if name is None:
            for module in self.modules.values():
                if "stop_thread" in dir(module) and callable(getattr(module,'stop_thread', None)):
                    module.stop_thread()
            return True

        elif name in self.modules:
            self.modules[name].stop_thread()
            return True
        
        return False
    
    def destruct(self, name=None):
        self.stop_mod(name)
        del self.modules[name]
        return False if self.exists(name) else True

    def restart(self, name):
        self.destruct(name)
        self.create(name)
        return True

    def exists(self, name:str) -> bool:
        return True if name in self.modules else False