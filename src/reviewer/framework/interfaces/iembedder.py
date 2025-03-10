from abc import ABC, abstractmethod

from ..dataset import Dataset 


class Embedder(ABC):

    @abstractmethod
    def embed(self, data: Dataset) -> Dataset:
        raise NotImplementedError("abstract method")

