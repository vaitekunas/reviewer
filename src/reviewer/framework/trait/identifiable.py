__all__ = ["get_object_id", "Identifiable"]

from abc import abstractmethod
from datetime import datetime
from typing import Any


def get_object_id(obj: Any) -> str:
    return f"{int(datetime.now().timestamp())}_{int(id(obj))}"

class Identifiable:

    def __init__(self) -> None:
        
        if not hasattr(self, "_id"):
            self._id = get_object_id(self)

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError("abstract method")

    @property
    def id(self) -> str:
        return self._id
