import threading
from collections import defaultdict

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
            callback(value)
    
    def get(self, topic, default=None):
        with self._lock:
            return self._data.get(topic, default)

    def subscribe(self, topic, callback):
        with self._lock:
            self._subs[topic].append(callback)