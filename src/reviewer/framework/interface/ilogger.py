__all__ = ["ILogger"]

from abc import ABC, abstractmethod


class ILogger(ABC):

    @abstractmethod
    def log(self, msg: str) -> None:
        raise NotImplementedError("abstract method")
