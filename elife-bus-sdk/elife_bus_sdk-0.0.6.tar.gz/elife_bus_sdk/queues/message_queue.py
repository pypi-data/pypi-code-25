from abc import ABC, abstractmethod
from typing import Any, Dict, Generator


class MessageQueue(ABC):

    @abstractmethod
    def dequeue(self) -> Any:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def enqueue(self, message: Dict) -> Any:
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    # pylint:disable=duplicate-code
    def name(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def poll(self) -> Generator[Dict, None, None]:
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def queue(self) -> Any:
        raise NotImplementedError  # pragma: no cover
