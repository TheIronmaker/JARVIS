

class ServoUpdaterView:
    def __init__(self, name, parent, settings):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        
        self.bus_global = parent.bus
        self.bus = parent.bus.namespaced(name)
    
    def poll(self):
        pass