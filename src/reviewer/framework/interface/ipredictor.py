__all__ = ["IPredictor"]

from abc import abstractmethod
from typing import TypeVar

from .imethod import IMethod
from .idataset import IDataset 
from .iconfig import IConfig

T = TypeVar('T', bound=IConfig)


class IPredictor(IMethod[T]):

    @abstractmethod
    def train(self, data: IDataset) -> None:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def predict(self, data: IDataset) -> IDataset:
        raise NotImplementedError("abstract method")

    @property
    @abstractmethod
    def is_trained(self) -> bool:
        raise NotImplementedError("abstract method")
