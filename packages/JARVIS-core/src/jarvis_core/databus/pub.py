import zmq
import time
import random

def publish():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    # Connect directly to the switchyard incoming track
    socket.connect("tcp://localhost:5555") 

    print("🛰️ Sensor node rolling out onto Track A...")
    
    while True:
        # Format: "Topic Data" (ZeroMQ filters by the first string)
        gyro_x = random.uniform(-1.0, 1.0)
        message = f"PI_GYRO {gyro_x:.4f}"
        
        socket.send_string(message)
        print(f"Sent: {message}")
        time.sleep(0.1)