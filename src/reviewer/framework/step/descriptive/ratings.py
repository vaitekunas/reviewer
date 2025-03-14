__all__ = ["RatingAnalyserConfig", "RatingAnalyser"]

import numpy as np
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Callable, Any, override
from unicodedata import name

from ...interface import IConfig, IDataset, IAnalyser
from ...aliases import AnalysisField, FieldSchema, ResultType, Result, NamedResults


@dataclass
class RatingAnalyserConfig(IConfig):

    input_field: str
    output_histogram_name: str
    output_quantile_name:  str
    quantiles:  list[float]
    min_rating: int
    max_rating: int
    fill_rating_gaps: bool

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RatingAnalyser(IAnalyser[RatingAnalyserConfig]):

    def __init__(self, 
                 config:  RatingAnalyserConfig | None = None) -> None:

        super().__init__(config)

        self._name   = "NgramAnalyser"
        self._config = config or self.get_default_config()

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> RatingAnalyserConfig:
        return RatingAnalyserConfig(input_field           = "rating",
                                    output_histogram_name = "rating_histogram",
                                    quantiles             = [0.05, 0.25, 0.50, 0.75, 0.95],
                                    output_quantile_name  = "rating_quantiles",
                                    min_rating            = 1,
                                    max_rating            = 5,
                                    fill_rating_gaps      = False)

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.input_field: FieldSchema(dtype = int, 
                                                      description = "Numerical rating of the review")}

    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {}

    # ResultCreator
    @override
    def get_required_results(self) -> dict[str, ResultType]:
        return {}

    @override
    def get_created_results(self) -> dict[str, ResultType]:
        return {self._config.output_histogram_name: ResultType.DATASET,
                self._config.output_quantile_name:  ResultType.DATASET}

    # Descriptive Analysis 
    @override
    def analyse(self, 
                data: IDataset, 
                results: NamedResults,
                new_dataset: Callable[[dict[str, list[Any]]], IDataset]) -> list[Result]:

        ratings = data.get_field_values(self._config.input_field)
        assert all([isinstance(x, int) for x in ratings]), "Not all ratings are numeric"

        new_results: list[Result] = []

        # Rating counts
        counter = [(k,v) for k,v in Counter(ratings).items()]
        if self._config.fill_rating_gaps:
            rfound = {x[0] for x in counter}
            for i in range(self._config.min_rating, self._config.max_rating+1):
                if i not in rfound:
                    counter.append((i, 0))

        counter = sorted(counter, key = lambda x: x[0])

        new_results.append(Result(method_id   = self.id,
                                  result_type = ResultType.DATASET,
                                  result_name = self._config.output_histogram_name,
                                  value       = new_dataset({"rating":    [x[0] for x in counter],
                                                             "frequency": [x[1] for x in counter]})))
        
        # Rating quantiles
        qs = np.quantile(ratings, self._config.quantiles)
        new_results.append(Result(method_id   = self.id,
                                  result_type = ResultType.DATASET,
                                  result_name = self._config.output_histogram_name,
                                  value       = new_dataset({"quantile": self._config.quantiles,
                                                             "value":    [float(x) for x in qs]})))

        return new_results

