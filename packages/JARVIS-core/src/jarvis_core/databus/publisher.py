import json
import zmq
import msgpack

class Publisher:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        # Local for now
        # May replace localhost with ip of any computer on network
        self.socket.connect("tcp://localhost:5555")

        self.REGISTRY = {
            'dict': self.ser_msgpack,
            'list': self.ser_msgpack,
            'tuple': self.ser_msgpack,
            'set': self.ser_set,
            'str': self.ser_string,
            'ndarray': self.ser_numpy
        }

    @staticmethod
    def ser_fallback(obj):
        return {"type": "bytes"}, bytes(obj)
    
    @staticmethod
    def ser_msgpack(d):
        # Universal binary format: faster and smaller than JSON
        return {"type": "msgpack"}, msgpack.packb(d)
    
    @staticmethod
    def ser_set(s):
        # Convert set to list, then serialize to cross-language binary array
        return {"type": "set"}, msgpack.packb(list(s))

    @staticmethod
    def ser_string(s):
        return {"type": "str"}, s.encode('utf-8')

    @staticmethod
    def ser_numpy(arr):
        return {"type": "numpy", "dtype": str(arr.dtype), "shape": arr.shape}, arr.tobytes()
        
    def send(self, data, channel:str=""):
        type_name = type(data).__name__
        serializer = self.REGISTRY.get(type_name, self.ser_fallback)
        metadata, payload = serializer(data)

        # Multi-part ZeroMQ message: Namespace, metadata, data
        self.socket.send_string(channel, flags=zmq.SNDMORE)
        self.socket.send_json(metadata, flags=zmq.SNDMORE)
        self.socket.send(payload, flags=0)
