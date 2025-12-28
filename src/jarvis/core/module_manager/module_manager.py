from jarvis.settings import settings

class ModuleManager:
    def __init__(self, bus):
        self.bus = bus
        self.mod = {}

    def create(self, name, cls):
        if name in self.mod:
            return False
        self.mod[name] = cls(self.bus)
        return True

    def bulk_create(self, mapping):
        for name, cls in mapping.items():
            self.create(name, cls)
        return True

    def start_mod(self, name=None):
        if name is None:
            for name, module in self.mod.items():
                if settings.get(name, {}).get("enabled"):
                    module.start_thread()
            return True
        
        elif name in self.mod and settings.get(name, {}).get("enabled"):
            self.mod[name].start_thread()
            return True

        return False

    def stop_mod(self, name=None):
        print("STOPPING")
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

    def restart(self, name, cls):
        self.destruct(name)
        self.create(name, cls)
        return True

    def exists(self, name:str) -> bool:
        return True if name in self.mod.keys() else False