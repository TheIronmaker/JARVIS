import threading
import time

from jarvis.modules import Camera, HandTracker, FaceTracker
from jarvis.app_core.app import run_app

shared_state = {
    "camera_display": None,    # combined frame with overlays
    "status": {},              # optional thread status info
    "camera_tracker": {}
}


def main_loop(modules, state):
    while True:
        frame = modules[0].img_rgb()
        modules[1].process_image(frame)
        modules[1].get_coordinates()
        overlay = modules[1].get_reading("Local")

        state["camera_display"] = modules[1].overlay_tracking(frame)
        state["camera_tracker"] = {"coordinates_overlay":overlay}



        # # Face Tracking
        # modules[2].process_image(frame)
        # state["camera_display"] = modules[2].overlay_tracking(frame)

        # # For status panel
        # state["status"]["cam_alive"] = cam.running
        # state["status"]["tracker_alive"] = tracker.running

        # Throttle update timing - to be refined
        time.sleep(0.01)

def main():   
    cam = Camera()
    hand_tracker = HandTracker()
    face_tracker = FaceTracker()
    modules = [cam, hand_tracker, face_tracker]

    for t in [modules[0]]: t.start()

    main_thread = threading.Thread(target=main_loop, args=(modules, shared_state), daemon=True)
    main_thread.start()

    run_app(shared_state)

    for t in [modules["cam"]]: t.stop()
    main_thread.join()

if __name__ == "__main__":
    main()
