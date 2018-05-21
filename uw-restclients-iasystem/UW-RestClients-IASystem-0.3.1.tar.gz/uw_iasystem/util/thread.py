import sys
from restclients_core.thread import Thread


class ThreadWithResponse(Thread):

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self.response = None
        self.exception = None

    def run(self):
        try:
            if sys.version_info[0] == 2:
                if self._Thread__target is not None:
                    self.response = self._Thread__target(
                        *self._Thread__args, **self._Thread__kwargs)
            else:
                if self._target:
                    self.response = self._target(
                        *self._args, **self._kwargs)
        except Exception as ex:
            self.exception = ex
