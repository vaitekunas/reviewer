__all__ = ["Runtime"]

from matplotlib.colors import Colormap, LinearSegmentedColormap
from typing import Any, Callable, Generator

from .interface import IDataset, IFigure

class Runtime:

    def __init__(self, 
                 dataset_constructor: Callable[[dict[str, Any]], IDataset],
                 figure_constructor: Callable[[Any], IFigure],
                 colors: list[str] | None = None) -> None:

        self._dataset_constructor = dataset_constructor
        self._figure_constructor  = figure_constructor

        self._colors = colors or ['#1D3557', '#457B9D', '#A8DADC', '#F1FAEE', '#E63946']

    def new_dataset(self, fields: dict[str, list[Any]]) -> IDataset:
        return self._dataset_constructor(fields)

    def new_figure(self, fig: Any) -> IFigure:
        return self._figure_constructor(fig)

    def _get_colors(self, step_size: float=0.1) -> Generator[str, None, None]:
        cmap = LinearSegmentedColormap.from_list("", self._colors)
        
        j = 0
        r = 2
        while True:
            iis = [step_size*j, 1-step_size*j]
            if min(iis) < 0 or max(iis) > 1:
                j = step_size/r
                r += 1 
                continue
            
            for i in iis:
                r, g, b, _ = cmap(i)
                yield f'#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}'

            j+=1

    @property
    def palette(self) -> Callable[[], Generator[str, None, None]]:
        return self._get_colors

    @property 
    def colormap(self) -> Colormap:
        return LinearSegmentedColormap.from_list("", self._colors)
