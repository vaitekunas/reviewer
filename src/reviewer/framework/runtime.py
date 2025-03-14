__all__ = ["Runtime"]

from typing import Any, Callable, override

from .interface import IRuntime, IDataset

class Runtime(IRuntime):

    def __init__(self, 
                 dataset_constructor: Callable[[dict[str, Any]], IDataset]) -> None:

        self._dataset_constructor = dataset_constructor

    @override
    def new_dataset(self, fields: dict[str, list[Any]]) -> IDataset:
        return self._dataset_constructor(fields)
