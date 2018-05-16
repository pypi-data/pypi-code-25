import inspect
import typing
import logging
from collections import deque
from functools import partial


class Pipe(object):
    order = -1

    def once(self):
        pass

    def __gt__(self, other):
        return self.order > other.order

    def __lt__(self, other):
        return self.order < other.order


class Signal(object):
    def __repr__(self):
        return f"Signal({self.signal_name}) from {self.sender}"

    def __init__(self, signal_name: str, sender: Pipe,
                 receivers: typing.Tuple[callable], signal_args, signal_kwargs):
        self.receivers = receivers
        self.signal_args = signal_args
        self.signal_kwargs = signal_kwargs
        self.signal_name = signal_name
        self.sender = sender
        self.logger = logging.getLogger(f"Signal(f{self.signal_name}, f{sender})")

    def call(self):
        for receiver in self.receivers:
            self.logger.debug("Calling %s" % receiver)
            # noinspection PySimplifyBooleanCheck
            if receiver(self.sender, *self.signal_args, **self.signal_kwargs) == True:
                break


class Plumber(object):
    logger = logging.getLogger("%s.Plumber" % __name__)
    pipes: typing.List = None
    queue: deque = None
    joints: typing.Dict[str, typing.Tuple[Pipe]] = None

    def __init__(self):
        self.pipes = []
        self.joints = {}
        self.queue = deque()

    # noinspection PyUnusedLocal
    def _add_emitter(self, name: str, emitter: callable):
        if name not in self.joints:
            self.joints[name] = tuple()

    def _add_receiver(self, name: str, receiver: callable):
        if name not in self.joints:
            self.joints[name] = tuple()
        self.joints[name] += (receiver,)

    def _emitter_stub(self, name: str, pipe: Pipe, *args, **kwargs):
        receivers = self.get_receivers(name)
        s = Signal(name, sender=pipe, receivers=receivers,
                   signal_args=args, signal_kwargs=kwargs)
        self._enqueue(s)

    def add_pipe(self, pipe: Pipe):
        self.pipes.append(pipe)
        pipe.order = len(self.pipes)
        for k, v in inspect.getmembers(pipe, predicate=inspect.ismethod):
            if k.startswith('emit_'):
                name = k[len('emit_'):]
                self.logger.info(f"{pipe} emits {name}")
                emitter_func = partial(self._emitter_stub, name, pipe)
                setattr(pipe, k, emitter_func)
                self._add_emitter(name, emitter_func)
        for k, v in inspect.getmembers(pipe, predicate=inspect.ismethod):
            if k.startswith('receive_'):
                name = k[len('receive_'):]
                self.logger.info(f"{pipe} receives {name}")
                self._add_receiver(name, v)

    def go(self):
        """ Start running.
            We will call .once() on each Pipe until exhausted.
        """
        self.logger.info(".go() starting")
        for p in self.pipes:
            self.logger.debug(".go() calling once on %s" % p)
            while p.once():
                self.loop()
        self.loop()
        assert len(self.queue) == 0
        self.logger.debug(".go() finished")

    def loop(self):
        self.logger.debug(".loop() starting")
        while len(self.queue) > 0:
            signal = self.queue.popleft()
            signal.call()
        self.logger.debug(".loop() finished")

    def get_receivers(self, name: str):
        return self.joints[name]

    def _enqueue(self, signal: Signal):
        self.logger.debug(f"Enqueue {signal}")
        self.queue.append(signal)
