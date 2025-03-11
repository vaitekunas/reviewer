from abc import ABC, abstractmethod
from typing import Any

class Config:

    @abstractmethod
    def get_config_dict(self) -> dict[str, Any]:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def update(self, values: dict[str, Any]) -> None:
        raise NotImplementedError("abstract method")


class Configurable(ABC):

    @abstractmethod
    def get_config(self) -> Config:
        raise NotImplementedError("abstract method")

    @abstractmethod
    def configure(self, config: Config) -> None:
        raise NotImplementedError("abstract method")


