__all__ = ["PreprocessorConfig", "Preprocessor"]

import re
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from dataclasses import asdict, dataclass
from typing import Any, override

from ...aliases import AnalysisField, FieldSchema
from ...interface import IConfig, IPreprocessor, IDataset


@dataclass
class PreprocessorConfig(IConfig):

    input_field:  str = "text"
    output_field: str = "text"

    language: str = "english"

    do_lowercase:          bool = True
    do_remove_stopwords:   bool = True
    do_remove_short:       bool = True
    do_remove_nonascii:    bool = True
    do_stem:               bool = True
    do_lemmatization:      bool = False
    do_remove_punctuation: bool = False

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Preprocessor(IPreprocessor[PreprocessorConfig]):
    
    def __init__(self, 
                 config:    PreprocessorConfig | None = None) -> None:

        super().__init__(config)

        self._name      = "Preprocessor"
        self._config    = config or self.get_default_config()
        self._stopwords = set(nltk_stopwords.words(self._config.language))

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> PreprocessorConfig:
        return PreprocessorConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.input_field: FieldSchema(dtype = str, 
                                                      description = "To be preprocessed text")}

    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        if self._config.input_field != (new_field := self._config.output_field):
            return {new_field: FieldSchema(dtype = str, 
                                           description = "Preprocessed text")}
        return {}

    # Preprocessor
    @override
    def preprocess(self, data: IDataset) -> IDataset:
        data = data.copy()

        cfg = self._config

        values = data.get_field_values(cfg.input_field)
    
        if cfg.do_remove_nonascii:
            values = [re.sub(r"","",str(x)) for x in values]

        if cfg.do_lowercase:
            values = [str(x).lower() for x in values]

        if cfg.do_remove_stopwords:
            for i, text in enumerate(values):
                values[i] = " ".join([w for w in word_tokenize(text) if w.lower() not in self._stopwords])

        if cfg.do_stem:
            stemmer = SnowballStemmer(language=self._config.language)

            for i, text in enumerate(values):
                values[i] = " ".join([stemmer.stem(w) for w in word_tokenize(text)])

        if cfg.do_lemmatization:
            lemmatizer = WordNetLemmatizer()

            for i, text in enumerate(values):
                values[i] = " ".join([lemmatizer.lemmatize(w) for w in word_tokenize(text)])

        if cfg.do_remove_punctuation:
            values = [re.sub(r"([^\w\s]|_)", " ", str(x)) for x in values]

        if cfg.do_remove_short:
            for i, text in enumerate(values):
                values[i] = " ".join([x for x in text.split() if len(x) >= 3])

        # Remove double spaces
        values = [re.sub(r"[ ]{2,}", " ", str(x)).strip() for x in values]

        data.set_field_values(cfg.output_field, values)

        return data

