__all__ = ["LinePlotConfig", "LinePlot"]

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import asdict, dataclass
from typing import Any, Generator, override, Callable

from ...interface import IConfig, IDataset, IFigure, IVisualizer
from ...aliases import AnalysisField, FieldSchema, Result, ResultName, ResultType


@dataclass 
class LinePlotConfig(IConfig):

    x_input_field:         str = "x"
    y_input_field:         str = "y"
    output_name:           str = "linegraph"

    title:                 str = "Line Graph"
    x_label:               str = "Label X"
    y_label:               str = "Label Y"
    x_tick_format:         str = "%.2f"
    y_tick_format:         str = "%.2f"
    marker:                str = "o"

    figure_width:          int = 800
    figure_height:         int = 600
    figure_bg:             str = "#FFFFFF"

    calculate_average_y:   bool = False

    use_result: str | None = None

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LinePlot(IVisualizer[LinePlotConfig]):

    def __init__(self, config: LinePlotConfig | None = None) -> None:
        super().__init__(config)

        self._name   = "LinePlot"
        self._config = config or self.get_default_config()

        self._markers = [".", "o", "x", "X", "+", "*", "s"]

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return super().name

    # Configurable
    @override
    def get_default_config(self) -> LinePlotConfig:
        return LinePlotConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        if self._config.use_result: 
            return {}

        return {self._config.x_input_field: FieldSchema(dtype = int | float,
                                                        description = "X-axis field"),

                self._config.y_input_field: FieldSchema(dtype = int | float, 
                                                        description = "Y-axis field")}

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
                  data:    IDataset, 
                  results: dict[str, Result],
                  palette: Generator[str, None, None],
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

        # Get average value
        if cfg.calculate_average_y:
            avg_x = {}
            for xi, yi in zip(x,y):
                if xi not in avg_x:
                    avg_x[xi] = []

                avg_x[xi].append(yi)

            means = {k: np.mean(v) for k,v in avg_x.items()}
            x = list(means.keys())
            y = list(means.values())

        color = palette.__next__()

        marker = cfg.marker if cfg.marker == "" or cfg.marker in self._markers else self._markers[0]

        x_tick_labels = [cfg.x_tick_format % xi for xi in x ]
        y_tick_labels = [cfg.y_tick_format % yi for yi in y ]
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(x, y, c=color)
        if marker:
            ax.scatter(x, y, marker=marker, c=color)

        ax.set_title(f"{cfg.title}")
        ax.set_xlabel(cfg.x_label)
        ax.set_ylabel(cfg.y_label)
        ax.set_xticks(x, labels = x_tick_labels)
        ax.set_yticks(y, labels = y_tick_labels)
        ax.spines[['right', 'top']].set_visible(False)
        plt.close(fig)

        return [Result(method_id   = self.id,
                       result_name = self._config.output_name,
                       result_type = ResultType.FIGURE,
                       value       = new_figure(fig))]

