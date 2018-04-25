from abc import ABC, abstractmethod
from typing import Any

from elife_bus_sdk.events import Event


class EventPublisher(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def publish(self, event: Event) -> Any:
        raise NotImplementedError  # pragma: no cover
