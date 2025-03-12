__all__ = ["IMetric"]

from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Any


@total_ordering
class IMetric(ABC):

    @abstractmethod
    def as_str(self) -> str:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        raise NotImplementedError("abstract method")
