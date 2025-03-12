__all__ = ["IEvaluator"]

from abc import abstractmethod
from typing import TypeVar

from .imethod import IMethod
from .idataset import IDataset
from .imetric import IMetric
from .iconfig import IConfig

T = TypeVar('T', bound=IConfig)

class IEvaluator(IMethod[T]):

    @abstractmethod
    def evaluate(self, data: IDataset) -> IMetric:
        raise NotImplementedError("abstract method")
