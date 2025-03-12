__all__ = ["IEmbedder"]

from abc import abstractmethod
from typing import TypeVar

from .imethod import IMethod
from .idataset import IDataset 
from .iconfig import IConfig

T = TypeVar('T', bound=IConfig)

class IEmbedder(IMethod[T]):

    @abstractmethod
    def embed(self, data: IDataset) -> IDataset:
        raise NotImplementedError("abstract method")

