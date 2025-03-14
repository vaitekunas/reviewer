__all__ = ["IResultCreator"]


from abc import ABC, abstractmethod
from ..aliases import ResultType, ResultName

class IResultCreator(ABC):

    @abstractmethod
    def get_required_results(self) -> dict[ResultName, ResultType]:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def get_created_results(self) -> dict[ResultName, ResultType]:
        raise NotImplementedError("abstract method")
