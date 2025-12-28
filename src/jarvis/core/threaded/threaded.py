import threading
from time import sleep

from jarvis.core.logger import Logger

class ThreadedResource:
    def __init__(self, cycle_time=0.01, name=None):
        self.cycle_time = cycle_time
        self.stop_event = threading.Event()
        self.thread = None
        self.running = False
        self.name = name or self.__class__.__name__

    def loop(self):
        """This is the basic functionality that an overriding loop should replicate"""
        while self.running:
            Logger.warning("Thread running with no directive")
            self.cycle_sleep
    
    def cycle_sleep(self):
        sleep(self.cycle_time)

    def start_thread(self):
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.loop)
            self.thread.start()

    def stop_thread(self):
        self.running = False

        if self.thread and self.thread != threading.current_thread():
            self.thread.join()
            if not self.thread.is_alive():
                Logger.info(f"Thread Shut down: {self.name}")
        try:
            self.close()
        except Exception as e:
            Logger.error(f"Module Cleanup failed in {self.name}: {e}")
    
    def close(self):
        pass