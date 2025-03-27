__all__ = ["IFigure"]

from abc import ABC, abstractmethod
from typing import Any


class IFigure(ABC):

    @abstractmethod
    def to_bytes(self) -> bytes:
        raise NotImplementedError("abstract method")

    @property
    @abstractmethod
    def raw(self) -> Any:
        raise NotImplementedError("abstract method")
