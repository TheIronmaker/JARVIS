from jarvis.settings import settings

class ModuleManager:
    def __init__(self, bus):
        self.bus = bus
        self.modules = {}

    def create(self, name, cls):
        if name in self.modules:
            return False
        self.modules[name] = cls(self.bus)
        return True

    def bulk_create(self, mapping):
        for name, cls in mapping.items():
            self.create(name, cls)
        return True

    def start(self, name=None):
        if name is None:
            for name, module in self.modules.items():
                if settings.get(name, {}).get("enabled"):
                    module.start()
            return True
        
        elif name in self.modules and settings.get(name, {}).get("enabled"):
            self.modules[name].start()
            return True

        return False

    def stop(self, name=None):
        if name is None:
            for module in self.modules.values():
                module.stop()
            return True

        elif name in self.modules:
            self.modules[name].stop()
            return True
        
        return False
    
    def destruct(self, name=None):
        if name is None:
            self.stop()
            return True

        module = self.modules.get(name)
        if not module:
            return False

        if module.running:
            module.stop()

        del self.modules[name]
        return True

    def restart(self, name, cls):
        module = self.modules.get(name)
        if module:
            module.stop()
        self.modules[name] = cls(self.bus)
        self.start_modules(name)
        return True