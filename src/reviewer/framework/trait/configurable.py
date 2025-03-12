__all__ = ["Configurable"]

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..interface import IConfig

T = TypeVar('T', bound=IConfig)

class Configurable(ABC, Generic[T]):

    @abstractmethod
    def get_default_config(self) -> T:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def get_config(self) -> T:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def configure(self, config: T) -> None:
        raise NotImplementedError("abstract method")


