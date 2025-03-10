from abc import abstractmethod

from .iconfig import Config
from .iserializable import Serializable


class Method(Serializable):

    @abstractmethod
    def get_config(self) -> Config:
        raise NotImplementedError("abstract method")

    def configure(config: Config) -> None:
        raise NotImplementedError("abstract method")


