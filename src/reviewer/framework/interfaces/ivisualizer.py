from abc import ABC, abstractmethod

from ..dataset import Dataset
from ..figure import Figure

class Visualizer(ABC):

    @abstractmethod
    def visualize(self, data: Dataset) -> Figure:
        raise NotImplementedError("abstract method")
