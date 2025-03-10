from abc import ABC, abstractmethod
from functools import total_ordering

@total_ordering
class Metric(ABC):

    @abstractmethod
    def as_str(self) -> str:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError("abstract method")

    @abstractmethod
    def __lt__(self, other):
        raise NotImplementedError("abstract method")
