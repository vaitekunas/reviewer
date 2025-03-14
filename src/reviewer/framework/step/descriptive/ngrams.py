__all__ = ["NgramAnalyserConfig", "NgramAnalyser"]

from string import punctuation
from nltk import word_tokenize
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Callable, override

from ...interface import IConfig, IDataset, IAnalyser
from ...aliases import AnalysisField, FieldSchema, ResultType, Result, NamedResults


@dataclass
class NgramAnalyserConfig(IConfig):

    input_field: str
    output_name: str
    ngram_range: tuple[int, int]
    max_ngrams:  int 

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class NgramAnalyser(IAnalyser[NgramAnalyserConfig]):

    def __init__(self, 
                 config:  NgramAnalyserConfig | None = None) -> None:

        super().__init__(config)

        self._name    = "NgramAnalyser"
        self._config  = config or self.get_default_config()

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> NgramAnalyserConfig:
        return NgramAnalyserConfig(input_field = "text",
                                   output_name = "ngrams",
                                   ngram_range = (1, 1),
                                   max_ngrams  = 50)

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.input_field: FieldSchema(dtype = str, 
                                                      description = "Text field to be analysed")}

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

        ngram_range = self._config.ngram_range
        punctuation_words = {x for x in punctuation}

        counter = Counter() 
        for text in texts:
            words = word_tokenize(text)

            for i in range(len(words)):
                for n in range(ngram_range[0]-1, ngram_range[1]):
                    if i >= n:
                        phrase_words = words[i-n:i+1]
                        if set(phrase_words) & punctuation_words:
                            continue

                        phrase = " ".join(phrase_words)
                        counter.update([phrase])

        ngrams = {k:v for (k,v) in counter.most_common(self._config.max_ngrams)}
        result = new_dataset({"ngram":     list(ngrams.keys()),
                              "frequency": list(ngrams.values())})

        return [Result(method_id   = self.id, 
                       result_name = self._config.output_name,
                       result_type = ResultType.DATASET,
                       value       = result)]

