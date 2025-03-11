from abc import ABC, abstractmethod


class Logger(ABC):

    @abstractmethod
    def log(self, msg: str) -> None:
        raise NotImplementedError("abstract method")
