__all__ = ["TSneVisualizationConfig", "TSneVisualization"]

import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from dataclasses import asdict, dataclass
from typing import Any, Generator, override, Callable

from ...interface import IConfig, IDataset, IFigure, IVisualizer
from ...aliases import AnalysisField, FieldSchema, Result, ResultName, ResultType


@dataclass 
class TSneVisualizationConfig(IConfig):

    category_field:         str = "y"
    embedding_field_prefix: str = "emb_"
    output_name:            str = "tsne"

    title:                  str = "t-SNE"
    perplexity:             int = 3

    marker:           str = "o"
    figure_width:     int = 800
    figure_height:    int = 600
    figure_bg:        str = "#FFFFFF"

    use_result: str | None = None

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TSneVisualization(IVisualizer[TSneVisualizationConfig]):

    def __init__(self, config: TSneVisualizationConfig | None = None) -> None:
        super().__init__(config)

        self._name   = "T-SNE"
        self._config = config or self.get_default_config()

        self._markers = [".", "o", "x", "X", "+", "*", "s"]

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return super().name

    # Configurable
    @override
    def get_default_config(self) -> TSneVisualizationConfig:
        return TSneVisualizationConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        if self._config.use_result: 
            return {}

        return {self._config.category_field: FieldSchema(dtype = Any,
                                                         description = "Category field"),

                self._config.embedding_field_prefix: FieldSchema(dtype = float,
                                                                 prefix = True,
                                                                 description = "Text embeddings")}

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
                  data: IDataset, 
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

        categories       = data.get_field_values(cfg.category_field)
        category_colors  = {x:p for p,x in zip(palette, sorted(set(categories)))}
        colors           = [category_colors[x] for x in categories]
        embedding_fields = [x for x in data.fields.keys() if x.startswith(cfg.embedding_field_prefix)]

        X = np.asarray([data.get_field_values(x) for x in embedding_fields]).T

        X_embedded = (TSNE(n_components  = 2, 
                           learning_rate = 'auto',
                           init          = 'random', 
                           perplexity    = cfg.perplexity)
                        .fit_transform(X))

        marker = cfg.marker if cfg.marker in self._markers else self._markers[0]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(X_embedded[:, 0], X_embedded[:, 1], marker=marker, c=colors)
        ax.set_title(f"{cfg.title}\n(perplexity: {cfg.perplexity:d})")
        ax.spines[['left', 'bottom', 'right', 'top']].set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        plt.close(fig)

        return [Result(method_id   = self.id,
                       result_name = self._config.output_name,
                       result_type = ResultType.FIGURE,
                       value       = new_figure(fig))]

