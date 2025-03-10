from abc import ABC, abstractmethod

from ..dataset import Dataset
from .imetric import Metric

class Evaluator(ABC):

    @abstractmethod
    def evaluate(self, data: Dataset) -> Metric:
        raise NotImplementedError("abstract method")
