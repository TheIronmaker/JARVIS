import threading
import time

from jarvis.modules import Camera, HandTracker
from jarvis.app_core.app import run_app

shared_state = {
    "camera_display": None,    # combined frame with overlays
    "status": {}               # optional thread status info
}


def main_loop(cam, state):
    while True:
        frame = cam.img_rgb() 
        #overlay = tracker.overlay
        #if overlay is not None:
        #   frame = overlay
        state["camera_display"] = frame

        #state["status"]["cam_alive"] = cam.running
        #state["status"]["tracker_alive"] = tracker.running

        # Maybe throttle update timing
        time.sleep(0.01)

def main():
    cam = Camera()
    #tracker = HandTracker()

    for t in [cam]: t.start()

    main_thread = threading.Thread(target=main_loop, args=(cam, shared_state), daemon=True)
    main_thread.start()

    run_app(shared_state)

    for t in [cam]: t.stop()
    main_thread.join()

if __name__ == "__main__":
    main()
