from jarvis.core.logger import Logger
from jarvis.core.threaded import ThreadedResource

class AtomSimNode(ThreadedResource):
    def __init__(self, name, bus):
        super().__init__(0.001)
        self.bus = bus.namespaced(name)