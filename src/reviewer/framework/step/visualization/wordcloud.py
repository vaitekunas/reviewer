__all__ = ["WordCloudConfig", "WordCloud"]

from matplotlib.colors import Colormap
import matplotlib.pyplot as plt
from wordcloud import WordCloud as WordCloudFigure
from dataclasses import asdict, dataclass
from typing import Any, Callable, Generator, override

from ...interface import IConfig, IDataset, IFigure, IVisualizer
from ...aliases import AnalysisField, FieldSchema, Result, ResultName, ResultType


@dataclass 
class WordCloudConfig(IConfig):

    input_field: str = "text"
    output_name: str = "word_cloud"
    title:       str = "Word Cloud"

    figure_width:     int = 800
    figure_height:    int = 600
    figure_bg:        str = "#FFFFFF"

    use_result: str | None = None

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class WordCloud(IVisualizer[WordCloudConfig]):

    def __init__(self, config: WordCloudConfig | None = None) -> None:
        super().__init__(config)

        self._name   = "Word cloud"
        self._config = config or self.get_default_config()

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> WordCloudConfig:
        return WordCloudConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        if self._config.use_result: 
            return {}

        return {self._config.input_field: FieldSchema(dtype = str,
                                                      description = "Text field")}

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

        target = data.get_field_values(self._config.input_field)
        text   = "\n".join(target)

        wordcloud = (WordCloudFigure(width            = cfg.figure_width, 
                                     height           = cfg.figure_height,
                                     colormap         = colormap,
                                     background_color = cfg.figure_bg)
                        .generate(text))

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        plt.close(fig)

        return [Result(method_id   = self.id,
                       result_name = self._config.output_name,
                       result_type = ResultType.FIGURE,
                       value       = new_figure(fig))]

