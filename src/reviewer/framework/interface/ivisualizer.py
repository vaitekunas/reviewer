__all__ = ["IVisualizer"]

from abc import abstractmethod
from typing import Any, Callable, Generator, TypeVar

from .imethod import IMethod
from .idataset import IDataset
from .ifigure import IFigure
from .iconfig import IConfig
from .iresultcreator import IResultCreator

from ..aliases import Result

T = TypeVar('T', bound=IConfig)


class IVisualizer(IMethod[T], IResultCreator):

    @abstractmethod
    def visualize(self, 
                  data:       IDataset, 
                  results:    dict[str, Result],
                  palette:    Generator[str, None, None],
                  new_figure: Callable[[Any], IFigure]) -> list[Result]:
        raise NotImplementedError("abstract method")
