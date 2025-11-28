from jarvis.modules.camera import Camera
import cv2
import time


def main():
    cam = Camera()
    cam.start()

    try:
        while True:
            cam.show_output()
            if cv2.waitKey(1) & 0xFF == 27: break
            time.sleep(0.001)
    finally:
        cam.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()