import threading
from collections import defaultdict

from jarvis.core.logger import Logger

class DataBus:
    def __init__(self):
        self._data = {}
        self._subs = defaultdict(list)
        self._lock = threading.Lock()

    def publish(self, topic, value):
        with self._lock:
            self._data[topic] = value
            subs = list(self._subs[topic])
        for callback in subs:
            try:
                callback(value)
            except Exception as e:
                Logger.error(f"Automatic function failed to run: {callback.__name__} with Exception: {e}")
    
    def publish_many(self, data:dict):
        for topic, value in data.items():
            self.publish(topic, value)
    
    def get(self, topic, default=None):
        with self._lock:
            return self._data.get(topic, default)

    def subscribe(self, topic, callback):
        with self._lock:
            self._subs[topic].append(callback)

    def exists(self, topic, default):
        return True if topic in self._data.keys() else default
    
    def namespaced(self, prefix):
        bus = self
        class NSBus:
            def publish(self, topic, value):
                bus.publish(f"{prefix}.{topic}", value)
            def publish_many(self, data):
                for topic, value in data.items():
                    self.publish(topic, value)
            def get(self, topic, default=None):
                return bus.get(f"{prefix}.{topic}", default)
            def exists(self, topic, default):
                return bus.exists(f"{prefix}.{topic}", default)
            def namespaced(self, subprefix):
                return bus.namespaced(f"{prefix}.{subprefix}")
        return NSBus()