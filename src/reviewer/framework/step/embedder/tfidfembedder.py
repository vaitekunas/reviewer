__all__ = ["TfIdfEmbedderConfig", "TfIdfEmbedder"]

import numpy as np
from dataclasses import asdict, dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from typing import Any, override

from ...interface import IEmbedder, IConfig, IDataset
from ...aliases import AnalysisField, FieldSchema


@dataclass
class TfIdfEmbedderConfig(IConfig):

    input_field:   str = "text"
    output_prefix: str = "emb_"
    ngram_range:   tuple[int, int] = (1, 1)

    max_features:       int  = 1024
    use_svd:            bool = True
    max_svd_components: int  = 128

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TfIdfEmbedder(IEmbedder[TfIdfEmbedderConfig]):

    def __init__(self, 
                 config:  TfIdfEmbedderConfig | None = None) -> None:

        super().__init__(config)

        self._name   = "TF-IDF-Embedder"
        self._config = config or self.get_default_config()
        self._is_trained = False

        self._tfidf = TfidfVectorizer(max_features = self._config.max_features)
        self._svd   = TruncatedSVD(n_components=self._config.max_svd_components)

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> TfIdfEmbedderConfig:
        return TfIdfEmbedderConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.input_field: FieldSchema(dtype = str, 
                                                      description = "To be preprocessed text")}

    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.output_prefix: FieldSchema(dtype = str, 
                                                        prefix = True,
                                                        description = "Embedding fields")}

    # Embedder
    @override
    def train(self, data: IDataset) -> None:
        if self.is_trained:
            return

        texts = data.train_data.get_field_values(self._config.input_field)

        if not self._is_trained:
            X_tfidf = self._tfidf.fit_transform(texts)

            if self._config.use_svd:
                self._svd.fit(X_tfidf)

        self._is_trained = True

    @override
    def embed(self, data: IDataset) -> IDataset:
        assert self._is_trained, "Embedder has not been trained yet"

        data = data.copy()

        texts = data.get_field_values(self._config.input_field)

        X_tfidf = self._tfidf.transform(texts)

        if self._config.use_svd:
            X_transform = self._svd.transform(X_tfidf)
        else:
            X_transform = X_tfidf

        assert isinstance(X_transform, np.ndarray), "Unexpected data type"

        for i in range(X_transform.shape[1]):
            data.set_field_values(f"{self._config.output_prefix}{i}", [float(x) for x in X_transform[:,i]])

        return data

    @property
    @override
    def is_trained(self) -> bool:
        return self._is_trained
