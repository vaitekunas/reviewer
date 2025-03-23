__all__ = ["TemporalNgramAnalyserConfig", "TemporalNgramAnalyser"]

from string import punctuation
from nltk import word_tokenize
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Callable, override

from ...interface import IConfig, IDataset, IAnalyser
from ...aliases import AnalysisField, FieldSchema, ResultType, Result, NamedResults


@dataclass
class TemporalNgramAnalyserConfig(IConfig):

    input_field: str  = "text"
    date_field:  str  = "date"
    output_name: str  = "ngrams"
    ngram_range: tuple[int, int] = (1, 1)
    max_ngrams:  int  = 50

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TemporalNgramAnalyser(IAnalyser[TemporalNgramAnalyserConfig]):

    def __init__(self, 
                 config:  TemporalNgramAnalyserConfig | None = None) -> None:

        super().__init__(config)

        self._name    = "TemporalNgramAnalyser"
        self._config  = config or self.get_default_config()

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> TemporalNgramAnalyserConfig:
        return TemporalNgramAnalyserConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.input_field: FieldSchema(dtype = str, 
                                                      description = "Text field to be analysed"),
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
        return {self._config.output_name: ResultType.DATASET}

    # Descriptive Analysis 
    @override
    def analyse(self, 
                data:        IDataset, 
                results:     NamedResults,
                new_dataset: Callable[[dict[str, list[Any]]], IDataset]) -> list[Result]:

        texts = data.get_field_values(self._config.input_field)
        dates = data.get_field_values(self._config.date_field)

        ngram_range = self._config.ngram_range
        punctuation_words = {x for x in punctuation}
        counters = {}

        for date, text in zip(dates, texts):
            if date not in counters:
                counters[date] = Counter()
        
            counter = counters[date]
            words = word_tokenize(text)

            for i in range(len(words)):
                for n in range(ngram_range[0]-1, ngram_range[1]):
                    if i >= n:
                        phrase_words = words[i-n:i+1]
                        if set(phrase_words) & punctuation_words:
                            continue

                        phrase = " ".join(phrase_words)
                        counter.update([phrase])

        c_dates  = []
        c_ngrams = []
        c_freqs  = []
        for date in sorted(list(set(dates))):
            counter = counters[date]
            ngrams  = {k:v for (k,v) in counter.most_common(self._config.max_ngrams)}

            c_dates  += [date] * len(ngrams)
            c_ngrams += list(ngrams.keys())
            c_freqs  += list(ngrams.values())


        result = new_dataset({"date":      c_dates,
                              "ngram":     c_ngrams,
                              "frequency": c_freqs})

        return [Result(method_id   = self.id, 
                       result_name = self._config.output_name,
                       result_type = ResultType.DATASET,
                       value       = result)]

