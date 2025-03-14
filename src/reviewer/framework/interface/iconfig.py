__all__ = ["IConfig"]

from abc import ABC, abstractmethod
from typing import Any


class IConfig(ABC):

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError("abstract method")

    def update(self, values: dict[str, Any]) -> None:
        for k, v in values.items():
            if hasattr(self, k):
                setattr(self, k, v)
