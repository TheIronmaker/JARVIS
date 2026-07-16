import zmq
import json

class Publisher:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        # Local for now
        self.socket.connect("tcp://localhost:5555")

        self.REGISTRY = {
            'dict': self.ser_dict,
            'list': self.ser_dict,
            'ndarray': self.ser_numpy
        }

    @staticmethod
    def ser_fallback(obj):
        return {"type": "bytes"}, bytes(obj)
    
    @staticmethod
    def ser_dict(d):
        return {"type": "json"}, json.dumps(d).encode('utf-8')
    
    @staticmethod
    def ser_numpy(arr):
        return {"type": "numpy", "dtype": str(arr.dtype), "shape": arr.shape}, arr.tobytes()
        
    def PUB(self, data):
        type_name = type(data).__name__
        serializer = self.REGISTRY.get(type_name, self.ser_fallback)
        metadata, payload = serializer(data)
        self.socket.send_json(metadata, flags=0)
        self.socket.send(payload)