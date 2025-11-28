import threading

class ThreadedResource:
    def __init__(self, sleep_time=0.01):
        self.running = False
        self.thread = None
        self.sleep_time = sleep_time

    def _loop(self):
        raise NotImplementedError

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            self.close()

    def close(self):
        pass