__all__ = ["IPreprocessor"]

from abc import abstractmethod
from typing import TypeVar

from .imethod import IMethod
from .idataset import IDataset
from .iconfig import IConfig

T = TypeVar('T', bound=IConfig)


class IPreprocessor(IMethod[T]):

    @abstractmethod
    def preprocess(self, data: IDataset) -> IDataset:
        raise NotImplementedError("abstract method")
