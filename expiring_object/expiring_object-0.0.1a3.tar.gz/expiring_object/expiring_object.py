from __future__ import print_function, with_statement

import time
import weakref

from threading import Thread
from collections import deque


class Dispatcher(Thread):
    """delete elements in thread in given expiring time
    """
    def __init__(self, expiring_time, maxlen=None):
        """
        :param expiring_time - lifetime of all objects
        :type expiring_time int

        :param maxlen - max length
        :type maxlen int None
        """
        super(Dispatcher, self).__init__()

        self.expiring_time = expiring_time
        self.container = deque(maxlen=maxlen)
        self._running = True

    def run(self):
        while self._running:
            if len(self.container) < 1:
                continue
            if self.container[0][1] <= time.time():
                if hasattr(self.container[0][0], '_handler'):
                    getattr(self.container[0][0], '_handler')()
                self.container.popleft()

    def add(self, obj):
        """add an element to a container"""
        self.container.append((obj, time.time() + self.expiring_time))

    def stop(self):
        """stop thread"""
        self._running = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def object_factory(obj, dp: Dispatcher):
    """Call a `weakref.proxy` on given object
    You shouldn't already have non weak references to this object"""
    dp.add(obj)
    return weakref.proxy(obj)
