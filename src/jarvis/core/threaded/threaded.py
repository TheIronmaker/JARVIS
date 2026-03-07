import threading
from time import sleep

from jarvis.core.logger import Logger

class ThreadedResource:
    def __init__(self, cycle_time=None, name=None, daemon=False):
        self.cycle_time = cycle_time or 0.01
        self.stop_event = threading.Event()
        self.thread = None
        self.daemon = daemon
        self.running = False
        self.name = name or self.__class__.__name__

    def is_running(self):
        return self.running and self.thread and self.thread.is_alive()
    
    def start_thread(self):
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.loop, daemon=self.daemon)
            self.thread.start()

    def stop_thread(self):
        self.running = False

        if self.thread and self.thread != threading.current_thread():
            self.thread.join()
            if not self.thread.is_alive():
                pass
                #Logger.info(f"Thread Shut down: {self.name}")
        try:
            self.close()
        except Exception as e:
            Logger.error(f"Module Cleanup failed in {self.name}: {e}")
    
    def close(self):
        pass

    def loop(self):
        """This is the basic functionality that an overriding loop should replicate"""
        while self.running:
            self.main_process()
            self.cycle_sleep()
    
    def main_process(self, *args):
        pass

    def cycle_sleep(self):
        sleep(self.cycle_time)