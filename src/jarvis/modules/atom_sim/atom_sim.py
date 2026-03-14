from jarvis.core.logger import Logger

class AtomSimNode:
    def __init__(self, name, bus):
        super().__init__(0.001)
        self.bus = bus.namespaced(name)