import threading

class Scheduler(threading.Thread):
    def __init__(self, **kwargs):
        super(Scheduler, self).__init__()
        self.interval = kwargs.get('interval', 4.)
        self.callback = kwargs.get('callback')
        self.running = threading.Event()
        self.waiting = threading.Event()
        self.stopped = threading.Event()
    def run(self):
        self.running.set()
        while self.running.is_set():
            self.waiting.wait(self.interval)
            if not self.waiting.is_set():
                cb = self.callback
                if cb is not None:
                    cb()
        self.stopped.set()
    def stop(self):
        self.running.clear()
        self.waiting.set()
        self.stopped.wait()
