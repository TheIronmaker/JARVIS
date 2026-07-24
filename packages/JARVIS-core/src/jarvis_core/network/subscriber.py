import zmq
import msgpack
import json
import numpy as np

class Subscriber:
    def __init__(self, channel:str=""):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        # For network access, use "tcp://*:5555"
        self.socket.bind("tcp://localhost:5555")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, channel)

        self.DESERIALIZER = {
            'json': lambda meta, payload: json.loads(payload.decode('utf-8')),
            'msgpack': lambda meta, payload: msgpack.unpackb(payload),
            'set': lambda meta, payload: set(msgpack.unpackb(payload)),
            'str': lambda meta, payload: payload.decode('utf-8'),
            'numpy': lambda meta, payload: np.frombuffer(payload, dtype=meta['dtype']).reshape(meta['shape']),
            'bytes': lambda meta, payload: payload
        }
    
    def debug_receive(self):
        raw_frames = self.socket.recv_multipart()
        print(f"Received a message with {len(raw_frames)} raw byte frames!")
        for i, frame in enumerate(raw_frames):
            print(f"  Frame {i}: {frame[:75].decode("utf-8")}")
        return None, None


    def receive(self):
        if self.socket.poll(timeout=0, flags=zmq.POLLIN):
            raw_frames = self.socket.recv_multipart()
            if len(raw_frames) < 3: return None

            incoming_channel = raw_frames[0].decode('utf-8')
            metadata = json.loads(raw_frames[1].decode('utf-8'))
            payload = raw_frames[2]

            data_type = metadata.get("type", "bytes")
            decoder = self.DESERIALIZER.get(data_type, lambda m, p: p)
            return decoder(metadata, payload)
    
        return None
