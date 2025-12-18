import threading
from time import sleep

from jarvis.modules.logger import Logger

class ThreadedResource:
    def __init__(self, cycle_time=0.01):
        self.enabled = False
        self.cycle_time = cycle_time
        self.thread = None

    def loop(self):
        while self.enabled:
            Logger.warning("Thread running with no directive")
            sleep(self.cycle_time)

    def start(self):
        if not self.enabled:
            self.enabled = True
            self.thread = threading.Thread(target=self.loop, daemon=True)
            self.thread.start()

    def stop(self):
        if self.enabled:
            self.enabled = False
            if self.thread and self.thread != threading.current_thread():
                self.thread.join()