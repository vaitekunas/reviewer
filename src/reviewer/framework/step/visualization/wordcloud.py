__all__ = ["WordCloudConfig", "WordCloud"]

import matplotlib.pyplot as plt
from wordcloud import WordCloud as WordCloudFigure
from dataclasses import asdict, dataclass
from typing import Any, Generator, override

from ...interface import IConfig, IDataset, IVisualizer
from ...aliases import AnalysisField, FieldSchema, Result, ResultName, ResultType


@dataclass 
class WordCloudConfig(IConfig):

    input_field: str = "text"
    output_name: str = "word_cloud"
    title:       str = "Word Cloud"

    figure_width:     int = 800
    figure_height:    int = 600
    figure_bg:        str = "#FFFFFF"

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
        return super().name

    # Configurable
    @override
    def get_default_config(self) -> WordCloudConfig:
        return WordCloudConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.input_field: FieldSchema(dtype = str,
                                                      description = "Text field")}

    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {}

    # Result creator
    @override
    def get_required_results(self) -> dict[ResultName, ResultType]:
        return {}

    @override
    def get_created_results(self) -> dict[ResultName, ResultType]:
        return {self._config.output_name: ResultType.FIGURE}

    # Visualizer
    @override
    def visualize(self, 
                  data:    IDataset, 
                  results: dict[str, Result],
                  palette: Generator[str, None, None]) -> list[Result]:

        data = data.copy()
        cfg = self._config

        target = data.get_field_values(self._config.input_field)
        text   = "\n".join(target)

        wordcloud = (WordCloudFigure(width            = cfg.figure_width, 
                                     height           = cfg.figure_height,
                                     background_color = cfg.figure_bg)
                        .generate(text))

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        plt.close(fig)

        return [Result(method_id   = self.id,
                       result_name = self._config.output_name,
                       result_type = ResultType.FIGURE,
                       value       = fig)]

