__all__ = ["IMethod"]

from abc import abstractmethod
from typing import TypeVar

from ..interface import IConfig
from ..trait import Identifiable, Configurable
from ..aliases import AnalysisField, FieldSchema

T = TypeVar('T', bound=IConfig)

class IMethod(Identifiable, Configurable[T]):

    @abstractmethod
    def __init__(self, config: T | None = None) -> None:
        super().__init__()

    @abstractmethod
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        raise NotImplementedError("abstract method")
