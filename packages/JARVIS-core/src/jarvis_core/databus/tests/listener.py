from jarvis_core.databus.subscriber import Subscriber

listener = Subscriber()
print("Listening to all broadcasted channels...")
while True:
    data = listener.debug_receive()