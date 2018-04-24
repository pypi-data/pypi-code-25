import threading
import time


class CallRate:
    def __init__(self, calls_count, seconds, wait=True):
        self._data = [time.time(), 0]
        self._lock = threading.Lock()
        self._calls_count = calls_count
        self._seconds = seconds
        self._wait = wait

    def __call__(self):
        with self._lock:
            if time.time() > self._data[0] + self._seconds:
                self._data = [time.time(), 1]
            elif self._calls_count > self._data[1]:
                self._data[1] = self._data[1] + 1
            else:
                if not self._wait:
                    raise Exception("To many calls")
                
                wait_time = self._data[0] + self._seconds - time.time()
                if wait_time > 0:
                    time.sleep(wait_time)
                    
                self._data = [time.time(), 1]
                