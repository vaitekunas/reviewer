from abc import abstractmethod
from typing import Any

from .iserializable import Serializable


class Config(Serializable):

    @abstractmethod
    def get_config_dict(self) -> dict[str, Any]:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def update(self, values: dict[str, Any]) -> None:
        raise NotImplementedError("abstract method")

