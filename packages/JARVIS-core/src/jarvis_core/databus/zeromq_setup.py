import zmq
import random
import sys
import asyncio

async def main():
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


async def publish():
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
        await asyncio.sleep(0.1)

async def subscribe():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    # Connect directly to the switchyard outgoing track
    socket.connect("tcp://localhost:5556")

    # Subscribe only to trains labeled "PI_GYRO"
    socket.setsockopt_string(zmq.SUBSCRIBE, "PI_GYRO")
    print("🖥️ 3D UI waiting at Track X for gyro data...")

    while True:
        message = socket.recv_string()
        print(f"Received data for 3D render: {message}")


if __name__ == "__main__":
    args = sys.argv

    if '-m' in args:
        asyncio.run(main())
    if '-p' in args:
        asyncio.run(publish())
    if '-s' in args:
        asyncio.run(subscribe())
