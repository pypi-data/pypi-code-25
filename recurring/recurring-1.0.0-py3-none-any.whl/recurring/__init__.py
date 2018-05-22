"""Simple library for running a callable every N seconds

job(callable, seconds) will call `callable` every `seconds` seconds in a dedicated thread. Other than at program exit,
the thread is only destroyed when `job.stop` is called or when changing the number of seconds in between calls with
`job.rate = new_seconds`.

Example:

    import recurring
    j = recurring.job(some_callable, some_seconds)
    j.start()
    # ...
    j.rate = some_new_seconds
    # ...
    j.stop()
"""


import sched
import threading

from typing import Callable


class _Scheduler(threading.Thread):
    """Thread dedicated to calling `self.task` every `self.rate` seconds."""

    def __init__(self, rate: int, task: Callable) -> None:
        """Initialize our scheduling and calling thread.



        Args:
            rate (int): How often, in seconds, to schedule calls.
            task (Callable): What to call, must be of 0 arguments
        """
        super().__init__(daemon=True)
        self._rate = rate
        self._task = task
        self._scheduler = sched.scheduler()

    @property
    def rate(self):
        """int: seconds in between calls."""
        return self._rate

    def run(self):
        """Part of Thread's api, not intended to be called by users."""
        self._queue()

    def stop(self):
        """Don't make or schedule any calls until further notice."""
        self._scheduler.cancel(self._next_call)

    def _call_and_queue(self) -> None:
        self._task()
        self._queue()

    def _queue(self) -> None:
        self._next_call = self._scheduler.enter(self._rate, 1, self._call_and_queue)
        self._scheduler.run()


class job:
    """A job is something that is called repeatedly and the time to wait in between calls."""

    def __init__(self, func: Callable, rate: int) -> None:
        """Create a job.

        Args:
            func (Callable): What to call, a function of 0 arguments.
            rate (int): Seconds in between calls.
        """
        self._func = func
        self._rate = rate
        self._scheduler = None

    def start(self) -> None:
        """Start calling our regularly-scheduled function"""
        if self._scheduler is None:
            self._scheduler = _Scheduler(self._rate, self._func)
        self._scheduler.start()

    def stop(self, timeout=None) -> None:
        """Don't make any more calls until further notics"""
        self._scheduler.stop()
        self._scheduler.join(timeout)
        self._scheduler = None

    @property
    def rate(self) -> int:
        """int: seconds in between calls

        When set, our internal scheduler is destroyed and recreated. This is a thread join and start under the hood.
        """
        return self._rate

    @rate.setter
    def rate(self, seconds: int) -> None:
        self.stop()
        self._rate = seconds
        self.start()

    def __str__(self):
        return f"{self.__class__.__qualname__}(rate={self._rate}, func={self._func})"
