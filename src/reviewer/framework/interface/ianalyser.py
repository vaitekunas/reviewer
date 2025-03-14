__all__ = ["IAnalyser"]

from abc import abstractmethod
from typing import TypeVar, Any, Callable

from .imethod import IMethod
from .idataset import IDataset 
from .iconfig import IConfig
from .iresultcreator import IResultCreator

from ..aliases import Result

T = TypeVar('T', bound=IConfig)


class IAnalyser(IMethod[T], IResultCreator):

    @abstractmethod
    def analyse(self, 
                data: IDataset, 
                results: dict[str, Result],
                new_dataset: Callable[[dict[str, list[Any]]], IDataset]) -> list[Result]:
        raise NotImplementedError("abstract method")

