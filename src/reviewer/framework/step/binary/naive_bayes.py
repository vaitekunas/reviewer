__all__ = ["NaiveBayesConfig", "NaiveBayes"]

import numpy as np
from dataclasses import dataclass
from typing import override
from sklearn.naive_bayes import GaussianNB

from ...interface import IDataset
from .classifier import *


@dataclass
class NaiveBayesConfig(BinaryClassifierConfig):
    pass

class NaiveBayes(BinaryClassifier):
    
    def __init__(self, config: NaiveBayesConfig | None = None) -> None:
        super().__init__(config)

        self._name       = "Naive Bayes"
        self._config     = config or self.get_default_config()

        self._model      = GaussianNB()
        self._is_trained = False

    @override
    def get_default_config(self) -> NaiveBayesConfig:
        return NaiveBayesConfig()

    # Predictor
    @override
    def train(self, data: IDataset) -> None:
        target, regressors = self._get_regressors(data.train_data)

        y = np.asarray(target)
        X = np.asarray(regressors).T

        self._model.fit(X, y)
        self._is_trained = True

    @override
    def predict(self, data: IDataset) -> IDataset:
        assert self._is_trained, "Model is has not been trained"

        data = data.copy()

        _, regressors = self._get_regressors(data)

        X = np.asarray(regressors).T

        y_probs = [float(x) for x in self._model.predict(X)]
        y_class = [int(x >= self._config.classification_threshold) for x in y_probs]

        data.set_field_values(self._config.output_prob_field,  y_probs)
        data.set_field_values(self._config.output_class_field, y_class)

        return data

