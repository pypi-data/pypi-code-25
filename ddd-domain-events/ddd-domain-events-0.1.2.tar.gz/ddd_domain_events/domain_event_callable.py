import abc
from enum import Enum
from typing import Callable, Type


class DomainEventCallable:
    def __init__(self, event_type: Type[Enum], callback: Callable):
        self.event_type = event_type
        self.callback = callback

    def __call__(self, *args, **kwargs):
        self.callback(*args, **kwargs)
