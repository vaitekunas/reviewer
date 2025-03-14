__all__ = ["IEvaluator"]

from abc import abstractmethod
from typing import TypeVar

from .imethod import IMethod
from .idataset import IDataset
from .iconfig import IConfig
from .iresultcreator import IResultCreator

from ..aliases import Result

T = TypeVar('T', bound=IConfig)

class IEvaluator(IMethod[T], IResultCreator):

    @abstractmethod
    def evaluate(self, data: IDataset, results: dict[str, Result]) -> list[Result]:
        raise NotImplementedError("abstract method")
