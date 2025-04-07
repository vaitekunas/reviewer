__all__ = ["ScatterPlotConfig", "ScatterPlot"]

from matplotlib.colors import Colormap
import matplotlib.pyplot as plt
from dataclasses import asdict, dataclass
from typing import Any, Generator, override, Callable

from matplotlib.ticker import FormatStrFormatter

from ...interface import IConfig, IDataset, IFigure, IVisualizer
from ...aliases import AnalysisField, FieldSchema, Result, ResultName, ResultType


@dataclass 
class ScatterPlotConfig(IConfig):

    x_input_field:         str = "x"
    y_input_field:         str = "y"
    category_field:        str = ""
    output_name:           str = "scatter"

    title:                 str = "Scatter plot"
    x_label:               str = "Label X"
    y_label:               str = "Label Y"
    x_tick_format:         str = "%.2f"
    y_tick_format:         str = "%.2f"
    marker:                str = "o"

    figure_width:          int = 800
    figure_height:         int = 600
    figure_bg:             str = "#FFFFFF"

    use_result: str | None = None

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ScatterPlot(IVisualizer[ScatterPlotConfig]):

    def __init__(self, config: ScatterPlotConfig | None = None) -> None:
        super().__init__(config)

        self._name   = "ScatterPlot"
        self._config = config or self.get_default_config()

        self._markers = [".", "o", "x", "X", "+", "*", "s"]

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> ScatterPlotConfig:
        return ScatterPlotConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        if self._config.use_result: 
            return {}

        required = {self._config.x_input_field: FieldSchema(dtype = int | float,
                                                            description = "X-axis field"),

                   self._config.y_input_field: FieldSchema(dtype = int | float, 
                                                           description = "Y-axis field")}

        if self._config.category_field:
            required[self._config.category_field] =  FieldSchema(dtype = Any,
                                                                 description = "Category field")

        return required
                
    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {}

    # Result creator
    @override
    def get_required_results(self) -> dict[ResultName, ResultType]:
        if not self._config.use_result:
            return {}

        if (name_parts := self._config.use_result.split(".")) == 1:
            return {self._config.use_result: ResultType.DATASET}
        else:
            return {name_parts[0]: ResultType.DATASET_DICT}

    @override
    def get_created_results(self) -> dict[ResultName, ResultType]:
        return {self._config.output_name: ResultType.FIGURE}

    # Visualizer
    @override
    def visualize(self, 
                  data:       IDataset, 
                  results:    dict[str, Result],
                  palette:    Generator[str, None, None],
                  colormap:   Colormap,
                  new_figure: Callable[[Any], IFigure]) -> list[Result]:

        cfg = self._config

        if not cfg.use_result:
            data = data.copy()
        else:
            name_parts = cfg.use_result.split(".")
            if len(name_parts) == 1:
                result = results[cfg.use_result]
                data = result.value.copy()
            else:
                result = results[name_parts[0]].value
                if name_parts[1] not in result:
                    raise Exception(f"Missing result from DATASET_DICT: '{name_parts[1]}'")
                data = result[name_parts[1]].copy()

        x = data.get_field_values(cfg.x_input_field)
        y = data.get_field_values(cfg.y_input_field)

        if cfg.category_field:
            categories       = [] if not cfg.category_field else data.get_field_values(cfg.category_field)
            category_colors  = {x:p for p,x in zip(palette, sorted(set(categories)))}
            colors           = [category_colors[x] for x in categories]
        else:
            colors = [palette.__next__()] * len(x)

        marker = cfg.marker if cfg.marker in self._markers else self._markers[0]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(x, y, marker=marker, c=colors)
        ax.set_title(f"{cfg.title}")
        ax.set_xlabel(cfg.x_label)
        ax.set_ylabel(cfg.y_label)

        ax.xaxis.set_major_formatter(FormatStrFormatter(cfg.x_tick_format))
        ax.yaxis.set_major_formatter(FormatStrFormatter(cfg.y_tick_format))

        ax.spines[['right', 'top']].set_visible(False)
        plt.close(fig)

        return [Result(method_id   = self.id,
                       result_name = self._config.output_name,
                       result_type = ResultType.FIGURE,
                       value       = new_figure(fig))]

