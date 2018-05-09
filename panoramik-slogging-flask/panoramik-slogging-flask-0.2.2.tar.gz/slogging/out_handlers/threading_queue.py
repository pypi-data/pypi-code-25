from datetime import datetime
from threading import Event, Thread

from six.moves import queue


# fix for uwsgi
# https://stackoverflow.com/questions/24098318/flask-background-thread-sees-a-non-empty-queue-as-empty
try:
    # noinspection PyPackageRequirements
    from uwsgidecorators import postfork
except ImportError:
    # not uwsgi
    def postfork(func):
        return func


class ThreadingQueueOutHandler:
    def __init__(self, sender):
        self._sender = sender

        self._send_queue = None
        self._thread = None
        self._stop_event = None

        @postfork
        def init():
            self._send_queue = queue.Queue()
            self._thread = Thread(target=self._handle_block)
            self._thread.daemon = True  # not pass as kwarg to Thread __init__ because of Python 2 compatibility
            self._stop_event = Event()

        init()

    def __del__(self):
        if self._stop_event is not None:
            self._stop_event.set()

    def _handle_block(self):
        while not self._stop_event.is_set() or not self._send_queue.empty():
            t = self._send_queue.get(block=True)
            if t is not None:
                self._sender.send(*t)

    def start(self):
        @postfork
        def start():
            self._thread.start()

        start()

    def stop(self, block=False):
        if self._stop_event is not None:
            self._stop_event.set()
            self._send_queue.put(None)  # to wake up thread
            if block:
                self._thread.join()  # wait for all events to be sent

    def queue_event(self, event, data, timestamp=None):
        if self._send_queue is not None:
            if timestamp is None:
                timestamp = datetime.utcnow()  # set now to preserve original event emit date
            self._send_queue.put((event, data, timestamp))
