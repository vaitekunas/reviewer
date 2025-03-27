__all__ = ["Runtime"]

from typing import Any, Callable, Generator

from .interface import IDataset, IFigure

class Runtime:

    def __init__(self, 
                 dataset_constructor: Callable[[dict[str, Any]], IDataset],
                 figure_constructor: Callable[[Any], IFigure]) -> None:

        self._dataset_constructor = dataset_constructor
        self._figure_constructor  = figure_constructor

    def new_dataset(self, fields: dict[str, list[Any]]) -> IDataset:
        return self._dataset_constructor(fields)

    def new_figure(self, fig: Any) -> IFigure:
        return self._figure_constructor(fig)

    def _get_colors(self) -> Generator[str, None, None]:
        while True:
            yield "red"

    @property
    def palette(self) -> Callable[[], Generator[str, None, None]]:
        return self._get_colors
