__all__ = ["IVisualizer"]

from abc import abstractmethod
from typing import TypeVar

from .imethod import IMethod
from .idataset import IDataset
from .ifigure import IFigure
from .iconfig import IConfig

T = TypeVar('T', bound=IConfig)


class IVisualizer(IMethod[T]):

    @abstractmethod
    def visualize(self, data: IDataset) -> IFigure:
        raise NotImplementedError("abstract method")
