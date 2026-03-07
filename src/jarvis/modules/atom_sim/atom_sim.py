from jarvis.core.logger import Logger
from jarvis.core.threaded import ThreadedResource

class AtomSimNode(ThreadedResource):
    def __init__(self, name, bus, settings):
        super().__init__(settings.get("cycle_time"))
        self.bus = bus.namespaced(name)
        self.settings = settings