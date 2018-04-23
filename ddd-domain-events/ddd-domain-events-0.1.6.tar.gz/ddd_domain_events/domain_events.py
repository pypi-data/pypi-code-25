import threading
from contextlib import ContextDecorator
from enum import Enum
from typing import Type
from collections import defaultdict

from ddd_domain_events.domain_event_callable import DomainEventCallable


class MissingDomainEventsContext(Exception):
    """Error raised whenever register_event is called outside of a Domain Events context"""


class DomainEvents(ContextDecorator):
    _actions = threading.local()

    def __enter__(self):
        if not hasattr(self._actions, 'events_by_type'):
            self._actions.events_by_type = defaultdict(list)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._actions.events_by_type
        return False

    def register_event(self, domain_event_callable: DomainEventCallable):
        if not hasattr(self._actions, 'events_by_type'):
            raise MissingDomainEventsContext('register_event cannot be called outside of a Domain Events context')
        self._actions.events_by_type[domain_event_callable.event_type].append(domain_event_callable)

    @classmethod
    def raise_event(cls, event_type: Type[Enum], *args, **kwargs):
        events_by_type = getattr(cls._actions, 'events_by_type', defaultdict(list))
        for domain_event_callable in events_by_type[event_type]:
            domain_event_callable(*args, **kwargs)



