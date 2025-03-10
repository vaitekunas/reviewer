from abc import ABC, abstractmethod

from ..dataset import Dataset 

class DataMapper(ABC):

    @abstractmethod
    def filter(self, data: Dataset) -> Dataset:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def map(self, data: Dataset) -> Dataset:
        raise NotImplementedError("abstract method")
