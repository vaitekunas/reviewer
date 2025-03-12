from abc import abstractmethod
from datetime import datetime


class Identifiable:

    def __init__(self) -> None:
        
        if not hasattr(self, "_id"):
            self._id = f"{int(datetime.now().timestamp())}_{int(id(self))}"

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError("abstract method")

    @property
    def id(self) -> str:
        return self._id
