__all__ = ["Runtime"]

from typing import Any, Callable, Generator

from .interface import IDataset

class Runtime:

    def __init__(self, 
                 dataset_constructor: Callable[[dict[str, Any]], IDataset]) -> None:

        self._dataset_constructor = dataset_constructor

    def new_dataset(self, fields: dict[str, list[Any]]) -> IDataset:
        return self._dataset_constructor(fields)

    def _get_colors(self) -> Generator[str, None, None]:
        while True:
            yield "red"

    @property
    def palette(self) -> Callable[[], Generator[str, None, None]]:
        return self._get_colors
