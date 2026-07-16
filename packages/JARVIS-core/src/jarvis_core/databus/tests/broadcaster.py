import time
from jarvis_core.databus.publisher import Publisher

broadcaster = Publisher()
while True:
    print("Broadcasting data:", time.time(), "to channel: xyz.abc")
    broadcaster.send(str("Current UTC: " + str(time.time())), channel="xyz.abc")
    time.sleep(0.1)