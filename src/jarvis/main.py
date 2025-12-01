import threading
import time

from jarvis.modules import Camera, HandTracker
from jarvis.app_core.app import run_app

shared_state = {
    "camera_display": None,    # combined frame with overlays
    "status": {}               # optional thread status info
}


def main_loop(cam, hand_tracker, state):
    while True:
        frame = cam.img_rgb()
        #overlay = tracker.overlay
        #if overlay is not None:
        #   frame = overlay
        hand_tracker.process_image(frame)
        frame = hand_tracker.overlay_tracking()
        state["camera_display"] = frame #hand_tracker.results

        #state["status"]["cam_alive"] = cam.running
        #state["status"]["tracker_alive"] = tracker.running

        # Maybe throttle update timing
        time.sleep(0.01)

def main():
    cam = Camera()
    hand_tracker = HandTracker()

    for t in [cam]: t.start()

    main_thread = threading.Thread(target=main_loop, args=(cam, hand_tracker, shared_state), daemon=True)
    main_thread.start()

    run_app(shared_state)

    for t in [cam]: t.stop()
    main_thread.join()

if __name__ == "__main__":
    main()
