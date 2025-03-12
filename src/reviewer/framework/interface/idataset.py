__all__ = ["IDataset"]

from abc import ABC, abstractmethod
from typing import Any, Type


class IDataset(ABC):

    @abstractmethod
    def apply_filter(self, sql_rule: str) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @abstractmethod
    def map_column(self, name: str, mapped_name: str) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @abstractmethod
    def verify_schema(self, name: str, dtype: Type[Any]) -> bool:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def drop_columns(self, columns: list[str]) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @property
    @abstractmethod
    def train_data(self) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @property
    @abstractmethod
    def test_data(self) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @abstractmethod
    def copy(self) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @property
    @abstractmethod
    def columns(self) -> dict[str, Type[Any]]:
        raise NotImplementedError("abstract method")

    @staticmethod
    @abstractmethod
    def from_path(path: str) -> 'IDataset':
        raise NotImplementedError("abstract method")




