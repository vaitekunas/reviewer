__all__ = ["IDataset"]

from abc import ABC, abstractmethod
from typing import Any, Type


class IDataset(ABC):

    @abstractmethod
    def apply_filter(self, sql_rule: str) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @abstractmethod
    def map_field(self, field: str, mapped_name: str) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @abstractmethod
    def verify_schema(self, field: str, dtype: Type[Any] | Any) -> bool:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def drop_fields(self, fields: list[str]) -> 'IDataset':
        raise NotImplementedError("abstract method")

    @abstractmethod
    def get_field_values(self, field: str) -> list[Any]:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def set_field_values(self, field: str, values: list[Any]) -> None:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def partition_train_data(self, train_part: float) -> None:
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
    def fields(self) -> dict[str, Type[Any]]:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def to_dict(self) -> dict[str, list[Any]]:
        raise NotImplementedError("abstract method")

    @staticmethod
    @abstractmethod
    def from_path(path: str) -> 'IDataset':
        raise NotImplementedError("abstract method")


