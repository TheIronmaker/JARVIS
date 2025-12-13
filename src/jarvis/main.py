import threading
import time

from jarvis.modules import Camera, HandTracker, FaceTracker
from jarvis.app_core.app import run_app

shared_state = {
    "camera_display": None,    # combined frame with overlays
    "status": {}               # optional thread status info
}


def main_loop(modules, state):
    while True:
        frame = modules["cam"].img_rgb()
        modules["hand_tracker"].process_image(frame)
        state["camera_display"] = modules["hand_tracker"].overlay_tracking(frame)
        modules["hand_tracker"].coordinates()

        #state["status"]["cam_alive"] = cam.running
        #state["status"]["tracker_alive"] = tracker.running

        # Throttle update timing - to be refined
        time.sleep(0.01)

def main():
    modules = {"cam":Camera(),
               "hand_tracker":HandTracker(),
               "face_tracker":FaceTracker()}

    for t in [modules["cam"]]: t.start()

    main_thread = threading.Thread(target=main_loop, args=(modules, shared_state), daemon=True)
    main_thread.start()

    run_app(shared_state)

    for t in [modules["cam"]]: t.stop()
    main_thread.join()

if __name__ == "__main__":
    main()
