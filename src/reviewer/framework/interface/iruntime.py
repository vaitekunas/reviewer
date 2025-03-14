__all__ = ["IRuntime"]

from typing import Any
from abc import ABC, abstractmethod

from .idataset import IDataset


class IRuntime(ABC):

    @abstractmethod
    def new_dataset(self, fields: dict[str, list[Any]]) -> IDataset:
        raise NotImplementedError("abstract method")
