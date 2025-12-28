from jarvis.core.threaded import ThreadedResource

class Module(ThreadedResource):
    def __init__(self, bus, name):
        super().__init__(daemon=True)
        self.name = name
        self.bus = bus
        self.running = False