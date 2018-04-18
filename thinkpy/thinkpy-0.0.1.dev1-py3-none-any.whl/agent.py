import logging
import threading

_DEBUG = False


class Logger:
    NAME = "think"
    FORMAT_STRING = "%(time)12.3f      %(source)-16s      %(message)s"
    LEVEL = logging.DEBUG

    @staticmethod
    def create(name=NAME, formats=FORMAT_STRING, level=LEVEL):
        """Returns a new logger."""
        logging.basicConfig(format=formats, level=level)
        return logging.getLogger(name)


class _ThreadInfo:
    RUNNING = 1
    TIMED_WAIT = 2
    EVENT_WAIT = 3
    NEXT = 4
    DONE = 5

    def __init__(self, index):
        self.index = index
        self.parent = threading.current_thread()
        self.status = _ThreadInfo.RUNNING
        self.requested_time = None
        self.last_think_time = -.001

    status_labels = {1: 'running', 2: 'timed_wait',
                     3: 'event_wait', 4: 'next', 5: 'done'}

    def __str__(self):
        return "{}: {} [{}, {}]".format(self.index, _ThreadInfo.status_labels[self.status],
                                        self.requested_time, self.last_think_time)


class Clock:

    def __init__(self, real_time=False, output=True):
        self._time = 0.0
        self.time_lock = threading.Lock()
        self.real_time = real_time
        self.threads = {}
        self.threads_lock = threading.Lock()
        self.event_flag = False
        self.barrier = threading.Barrier(0, lambda: self.update_all())
        self.barrier_lock = threading.Lock()
        if isinstance(output, logging.Logger):
            self.logger = output
        elif output:
            self.logger = Logger.create()
        else:
            self.logger = None

    def advance(self, dt):
        with self.time_lock:
            self._time += dt

    def time(self):
        with self.time_lock:
            return self._time

    def set(self, time):
        with self.time_lock:
            self._time = time

    def register(self, thread):
        with self.threads_lock:
            self.threads[thread] = _ThreadInfo(len(self.threads) + 1)
            if _DEBUG:
                self.debug("register thread: " + thread.name)
        with self.barrier_lock:
            self.barrier._parties = self.barrier._parties + 1
            if _DEBUG:
                self.debug("({} threads in barrier)".format(
                    self.barrier.parties))

    def n_threads(self):
        with self.threads_lock:
            return len(self.threads)

    def n_children(self, parent=None):
        if parent is None:
            parent = threading.current_thread()
        with self.threads_lock:
            count = 0
            for info in self.threads.values():
                if info.parent == parent:
                    count += 1
            return count

    def thread_index(self, thread=None):
        if thread is None:
            thread = threading.current_thread()
        with self.threads_lock:
            return self.threads[thread].index

    def deregister(self):
        with self.threads_lock:
            self.threads[threading.current_thread()].status = _ThreadInfo.DONE
        self.barrier.wait()

    def report_think(self):
        with self.threads_lock:
            self.threads[threading.current_thread(
            )].last_think_time = self.time()
        if _DEBUG:
            self.debug("reported think")

    def report_event(self):
        self.event_flag = True
        if _DEBUG:
            self.debug("reported event")

    def wait_for_next_event(self):
        with self.threads_lock:
            info = self.threads[threading.current_thread()]
            info.status = _ThreadInfo.EVENT_WAIT
        self._wait_my_turn()

    def wait_until(self, time):
        with self.threads_lock:
            info = self.threads[threading.current_thread()]
            info.status = _ThreadInfo.TIMED_WAIT
            info.requested_time = time
        self._wait_my_turn()

    def _wait_my_turn(self):
        if _DEBUG:
            self.debug("waiting at barrier...")
        self.barrier.wait()
        while not self._is_running(threading.current_thread()):
            self.barrier.wait()

    def _is_running(self, thread):
        with self.threads_lock:
            return self.threads[thread].status == _ThreadInfo.RUNNING

    def _debug_threads(self):
        for thread, info in self.threads.items():
            self.debug("[{}] -> {}".format(thread.name, info))

    def update_all(self):
        with self.threads_lock:
            if _DEBUG:
                self.debug("updating: event_flag = {}".format(self.event_flag))
                self.debug("-----")
                self._debug_threads()

            dones = []
            for thread, info in self.threads.items():
                if info.status == _ThreadInfo.DONE:
                    dones.append(thread)
            for thread in dones:
                del self.threads[thread]
                if _DEBUG:
                    self.debug("deleting thread [{}]".format(thread.name))
                with self.barrier_lock:
                    self.barrier._parties = self.barrier._parties - 1

            if (self.event_flag):
                self.event_flag = False
                self._change_status_locked(
                    _ThreadInfo.EVENT_WAIT, _ThreadInfo.NEXT)
            count = self._run_next_threads_locked()
            if count == 0:
                self._run_timed_threads_locked()
            if _DEBUG:
                self.debug("--> [t={}]".format(self.time()))
                self._debug_threads()
                self.debug("-----")

    def _change_status_locked(self, old, new):
        count = 0
        for info in self.threads.values():
            if info.status == old:
                info.status = new
                count += 1
        return count

    def _run_next_threads_locked(self):
        min_time = None
        for info in self.threads.values():
            if info.status == _ThreadInfo.NEXT:
                time = info.last_think_time
                if min_time is None or time < min_time:
                    min_time = time
        if min_time is not None:
            count = 0
            for info in self.threads.values():
                if info.status == _ThreadInfo.NEXT and info.last_think_time <= min_time:
                    info.status = _ThreadInfo.RUNNING
                    count += 1
            return count
        else:
            return 0

    def _run_timed_threads_locked(self):
        min_time = None
        for info in self.threads.values():
            if info.status == _ThreadInfo.TIMED_WAIT:
                time = info.requested_time
                if min_time is None or time < min_time:
                    min_time = time
        if min_time is not None:
            count = 0
            for info in self.threads.values():
                if info.status == _ThreadInfo.TIMED_WAIT and info.requested_time <= min_time:
                    info.status = _ThreadInfo.RUNNING
                    info.requested_time = None
                    count += 1
            self.set(min_time)
            return count
        else:
            return 0

    def wait_for_all(self):
        self.barrier.wait()
        while len(self.threads) > 1:
            if _DEBUG:
                self.debug("waiting for all...")
            self.barrier.wait()

    def log(self, message, source="clock"):
        if self.logger:
            self.logger.info(
                message, extra={'time': self.time(), 'source': source})

    def debug(self, message, source="clock"):
        if _DEBUG and self.logger:
            message = "[{}] {}".format(
                threading.current_thread().name, message)
            self.logger.debug(
                message, extra={'time': self.time(), 'source': source})


class Cancel:
    WILL_RUN = 1
    HAS_RUN = 2
    CANCELED = 3

    def __init__(self):
        self.status = Cancel.WILL_RUN
        self.lock = threading.Lock()

    def try_run(self):
        with self.lock:
            if self.status == Cancel.WILL_RUN:
                self.status = Cancel.HAS_RUN
                return True
            else:
                return False

    def try_cancel(self):
        with self.lock:
            if self.status == Cancel.WILL_RUN:
                self.status = Cancel.CANCELED
                return True
            else:
                return False


class Process:

    def __init__(self, name, clock=None):
        self.name = name
        self.clock = clock if clock is not None else Clock()

    def time(self):
        return self.clock.time()

    def run(self, action, delay=0.0):
        def _actions():
            if delay > 0:
                self.wait(delay)
            if action is not None:
                action()
            self.clock.deregister()
        thread = threading.Thread(target=_actions)
        self.clock.register(thread)
        thread.start()
        return thread

    def run_can_cancel(self, action, delay=0.0):
        cancel = Cancel()

        def _actions():
            if delay > 0:
                self.wait(delay)
            if cancel.try_run() and action is not None:
                action()
            self.clock.deregister()
        thread = threading.Thread(target=_actions)
        self.clock.register(thread)
        thread.start()
        return cancel

    def report_event(self):
        self.clock.report_event()

    def wait_for_next_event(self):
        self.clock.wait_for_next_event()

    def wait_until(self, time):
        self.clock.wait_until(time)

    def wait(self, seconds):
        self.wait_until(self.time() + seconds)

    def wait_for_all(self):
        self.clock.wait_for_all()

    def log(self, message, source=None):
        if source is None:
            source = self.name
        self.clock.log(message, source)

    def debug(self, message, source=None):
        if source is None:
            source = self.name
        self.clock.debug(message, source)


class Agent(Process):

    def __init__(self, name="agent", clock=None, output=True):
        super().__init__(name, clock if clock is not None else Clock(output=output))
        self.think_time = .050
        self.clock.register(threading.current_thread())
        self.think_worker = Worker("think", self)

    def indexed_name(self):
        name = self.name
        if self.clock.n_children() > 1:
            name += "[{}]".format(self.clock.thread_index())
        return name

    def think(self, message):
        self.think_worker.acquire()
        self.clock.report_think()
        self.log(message)
        self.wait_until(self.time() + self.think_time)
        self.think_worker.release()
        self.report_event()
        self.wait_for_next_event()


class Module(Process):

    def __init__(self, name, agent):
        super().__init__(name, agent.clock)
        self.agent = agent

    def think(self, message):
        self.agent.think(message)

    def log(self, message):
        super().log(message, self.agent.name + "." + self.name)

    def debug(self, message):
        super().debug(message, self.agent.name + "." + self.name)


class Worker:

    def __init__(self, name, process):
        self.name = name
        self.process = process
        self.lock = threading.Lock()

    def acquire(self):
        locked = self.lock.acquire(False)
        while not locked:
            if _DEBUG:
                self.process.debug(
                    "worker '{}' acquire failed".format(self.name))
            self.process.wait_for_next_event()
            locked = self.lock.acquire(False)
        if _DEBUG:
            self.process.debug("worker '{}' acquired".format(self.name))

    def run(self, delay=0.0, message=None, action=None, release=True):
        def _actions():
            if message is not None:
                self.process.log(message)
            if action is not None:
                action()
            if release:
                self.release()
        self.process.run(_actions, delay)

    def wait_until_free(self):
        locked = self.lock.acquire(False)
        while not locked:
            self.process.wait_for_next_event()
            locked = self.lock.acquire(False)
        self.lock.release()

    def release(self):
        self.lock.release()
        self.process.report_event()
        self.process.wait_for_next_event()
        if _DEBUG:
            self.process.debug("worker '{}' released".format(self.name))


class Buffer(Worker):

    def __init__(self, name, module):
        super().__init__(name, module)
        self.content_worker = Worker(name + "_content", module)
        self.contents = None

    def acquire(self):
        super().acquire()
        self.content_worker.acquire()
        if _DEBUG:
            self.process.debug("buffer '{}' acquired".format(self.name))

    def set(self, contents, delay=None, message=None, action=None):
        if delay is None:
            self.contents = contents
            self.content_worker.release()
        else:
            def _action():
                self.contents = contents
                self.content_worker.release()
                if action is not None:
                    action()
            self.content_worker.run(delay, message, _action, False)

    def clear(self, delay=None, message=None, action=None):
        self.set(None, delay, message, action)

    def wait_for_content(self):
        if _DEBUG:
            self.process.debug(
                "buffer '{}' waiting for content".format(self.name))
        self.content_worker.acquire()
        self.content_worker.release()

    def get_and_release(self):
        self.wait_for_content()
        result = self.contents
        if _DEBUG:
            self.process.debug("buffer '{}' released".format(self.name))
        super().release()
        return result
