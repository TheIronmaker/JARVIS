import threading
from time import sleep

from jarvis.core.logger import Logger

class ThreadedResource: #@revisit - rename variables with _
    def __init__(self, cycle_time=None, name=None, daemon=False):
        self.cycle_time = cycle_time or 0.008
        self.stop_event = threading.Event()
        self.thread = None
        self.daemon = daemon
        self.running = False
        self.name = name or self.__class__.__name__

    def _is_running(self):
        return self.running and self.thread and self.thread.is_alive()
    
    def _start_thread(self):
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._loop, daemon=self.daemon)
            self.thread.start()

    def _stop_thread(self):
        self.running = False

        if self.thread and self.thread != threading.current_thread():
            self.thread.join()
            if not self.thread.is_alive():
                pass
                #Logger.info(f"Thread Shut down: {self.name}")
        try:
            self._close()
        except Exception as e:
            Logger.error(f"Module Cleanup failed in {self.name}: {e}")
    
    def _close(self):
        pass

    def _loop(self):
        """This is the basic functionality that an overriding loop should replicate"""
        while self.running:
            self._main_process()
            self._cycle_sleep()
    
    def _main_process(self, *args):
        pass

    def _cycle_sleep(self):
        sleep(self.cycle_time)