import zmq
import json
import numpy as np

class Subscriber:
    def __init__(self, channel:str=""):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.bind("tcp://*:5555")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, channel)

        self.DESERIALIZER = {
            'json': lambda meta, payload: json.loads(payload.decode('utf-8')),
            'numpy': lambda meta, payload: np.frombuffer(payload, dtype=meta['dtype']).reshape(meta['shape']),
            'bytes': lambda meta, payload: payload
        }
    
    def RECIEVE(self):
        metadata = self.socket.recv_json()
        payload = self.socket.recv()

        data_type = metadata.get("type", "bytes")
        decoder = self.DESERIALIZER.get(data_type, lambda m, p: p)
        return decoder(metadata, payload)


def proxy():
    context = zmq.Context()

    # 1. Create the incoming track (where sensors connect to publish data)
    frontend = context.socket(zmq.XSUB)
    frontend.bind("tcp://*:5555")

    # 2. Create the outgoing track (where UIs connect to subscribe to data)
    backend = context.socket(zmq.XPUB)
    backend.bind("tcp://*:5556")

    print("🚂 Switchyard Operator is active. Tracks are locked into place...")
    
    # 3. Connect the tracks. ZeroMQ handles the rest automatically.
    zmq.proxy(frontend, backend)