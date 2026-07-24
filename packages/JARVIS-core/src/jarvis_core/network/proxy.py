import zmq

class Proxy:
    def __init__(self):
        pass

# Basic testing for communication hub
# The idea is that multiple things can connect to a central namespace/channel and distribute from there
def proxy():
    context = zmq.Context()

    # Create the incoming channel (where to publish data)
    frontend = context.socket(zmq.XSUB)
    frontend.bind("tcp://*:5555")

    # Create the outgoing channel (where to subscribe to data)
    backend = context.socket(zmq.XPUB)
    backend.bind("tcp://*:5556")

    print("Proxy Initialized...")
    zmq.proxy(frontend, backend)