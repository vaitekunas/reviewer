from abc import ABC, abstractmethod
from pandas import DataFrame


class Preprocessor(ABC):

    @abstractmethod
    def preprocess(self, data: DataFrame) -> DataFrame:
        raise NotImplementedError("abstract method")
