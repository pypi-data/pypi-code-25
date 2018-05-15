import uuid
from abc import abstractmethod


class ModContext:
    @abstractmethod
    def emit(self, id: uuid, message: dict) -> None:
        pass

    @abstractmethod
    def execute_blocking(self, callback, *args) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass
