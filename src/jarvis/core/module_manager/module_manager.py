from jarvis.settings import settings
from jarvis.core.logger import Logger
from jarvis.modules import *

class ModuleManager:
    def __init__(self, bus):
        self.bus = bus
        self.settings = settings.load("modules", paths=["settings"])
        self.mod = {}

        self.classes = {
            "camera": Camera,
            "hand_tracker": HandTracker,
            "face_tracker": FaceTracker
        }
    
    def load_modules(self):
        """Loads all modules in the modules.json settings file and creates the modules"""
        for config in self.settings.get("instances", []):
            module_type = config.get("type")
            if not module_type:
                Logger.error(f"Failed to retrieve default settings for module: {module_type}")
                continue
            self.create(module_type, config.get("name"), config)
        return True

    def bulk_create(self, mapping):
        for name, cls in mapping.items():
            self.create(name, cls)
        return True

    def create(self, module_type, module_name=None, config=None): # Needs bulk version
        module_name = module_name or module_type

        if module_name in self.mod:
            Logger.error(f"Failed to start {module_name} since a module already has that name")
            return False
        
        cls = self.classes.get(module_type)
        if cls is None:
            Logger.error(f"Module class does not exist: {module_type}")
            return False

        defaults = settings.load("defaults", [f"modules/{module_type}"])
        config = (defaults.copy() if config is None else settings.merge_settings(defaults, config))
        
        try:
            instance = cls(self.bus, settings=config)
            self.mod[module_name] = instance
        except:
            Logger.error(f"Unable to initialize module: {module_name}")

    def start_modules(self):
        return [self.start_module(name) for name in self.mod]

    def start_module(self, name):
        module = self.mod.get(name)
        if module and module.settings.get("enabled"):
            try:
                module.start_thread()
            except Exception:
                Logger.error(f"Unable to start thread for module: {name}")
            return True
        return False

    def stop_mod(self, name=None):
        if name is None:
            for module in self.mod.values():
                module.stop_thread()
            return True

        elif name in self.mod:
            self.mod[name].stop_thread()
            return True
        
        return False
    
    def destruct(self, name=None):
        self.stop_mod(name)
        del self.mod[name]
        return False if self.exists(name) else True

    def restart(self, name):
        self.destruct(name)
        self.create(name)
        return True

    def exists(self, name:str) -> bool:
        return True if name in self.mod.keys() else False