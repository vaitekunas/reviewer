from abc import ABC, abstractmethod
from typing import Any


class Serializable(ABC):

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        raise NotImplementedError("abstract method")
