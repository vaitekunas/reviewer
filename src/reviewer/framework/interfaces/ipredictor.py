from abc import ABC, abstractmethod

from ..dataset import Dataset 


class Predictor(ABC):

    @abstractmethod
    def train(self, data: Dataset) -> None:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def predict(self, data: Dataset) -> Dataset:
        raise NotImplementedError("abstract method")
