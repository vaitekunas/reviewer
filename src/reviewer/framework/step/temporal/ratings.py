__all__ = ["TemporalRatingAnalyserConfig", "TemporalRatingAnalyser"]

import numpy as np
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Callable, Any, override

from ...interface import IConfig, IDataset, IAnalyser
from ...aliases import AnalysisField, FieldSchema, ResultType, Result, NamedResults


@dataclass
class TemporalRatingAnalyserConfig(IConfig):

    input_field: str
    date_field:  str
    output_histogram_name: str
    output_quantile_name:  str
    quantiles:  list[float]
    min_rating: int
    max_rating: int
    fill_rating_gaps: bool

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TemporalRatingAnalyser(IAnalyser[TemporalRatingAnalyserConfig]):

    def __init__(self, 
                 config:  TemporalRatingAnalyserConfig | None = None) -> None:

        super().__init__(config)

        self._name   = "TemporalRatingAnalyser"
        self._config = config or self.get_default_config()

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> TemporalRatingAnalyserConfig:
        return TemporalRatingAnalyserConfig(input_field           = "rating",
                                            date_field            = "date",
                                            output_histogram_name = "rating_histogram",
                                            quantiles             = [0.05, 0.25, 0.50, 0.75, 0.95],
                                            output_quantile_name  = "rating_quantiles",
                                            min_rating            = 1,
                                            max_rating            = 5,
                                            fill_rating_gaps      = False)

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {
                self._config.input_field: FieldSchema(dtype = int, 
                                                      description = "Numerical rating of the review"),
                self._config.date_field: FieldSchema(dtype = str | int, 
                                                     description = "Date field")}

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
        dates   = data.get_field_values(self._config.date_field)
        assert all([isinstance(x, int) for x in ratings]), "Not all ratings are numeric"

        new_results: list[Result] = []

        # Partition per date
        date_ratings = {}
        for date, rating in zip(dates, ratings):
            if date not in date_ratings:
                date_ratings[date] = []

            date_ratings[date].append(rating)

        # Rating counts
        c_dates   = []
        c_ratings = []
        c_freqs   = []
        for date, dratings in date_ratings.items():
            counter = [(k,v) for k,v in Counter(dratings).items()]
            if self._config.fill_rating_gaps:
                rfound = {x[0] for x in counter}
                for i in range(self._config.min_rating, self._config.max_rating+1):
                    if i not in rfound:
                        counter.append((i, 0))

            counter = sorted(counter, key = lambda x: x[0])

            c_dates   += [date] * len(counter)
            c_ratings += [x[0] for x in counter]
            c_freqs   += [x[1] for x in counter]

        new_results.append(Result(method_id   = self.id,
                                  result_type = ResultType.DATASET,
                                  result_name = self._config.output_histogram_name,
                                  value       = new_dataset({"date":      c_dates,
                                                             "rating":    c_ratings,
                                                             "frequency": c_freqs})))
        
        # Rating quantiles
        c_dates     = []
        c_quantiles = []
        c_values    = []
        for date, dratings in date_ratings.items():
            qs = np.quantile(ratings, self._config.quantiles)

            c_dates     += [date] * len(qs)
            c_quantiles += self._config.quantiles
            c_values    += [float(x) for x in qs]

        new_results.append(Result(method_id   = self.id,
                                  result_type = ResultType.DATASET,
                                  result_name = self._config.output_histogram_name,
                                  value       = new_dataset({"date":     c_dates,
                                                             "quantile": c_quantiles,
                                                             "value":    c_values})))

        return new_results

