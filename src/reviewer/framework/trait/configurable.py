__all__ = ["Configurable"]

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..interface import IConfig

T = TypeVar('T', bound=IConfig)

class Configurable(ABC, Generic[T]):

    @abstractmethod
    def get_default_config(self) -> T:
        raise NotImplementedError("abstract method")

    def get_config(self) -> T:
        return self._config

    def configure(self, config: T) -> None:
        self._config = config


