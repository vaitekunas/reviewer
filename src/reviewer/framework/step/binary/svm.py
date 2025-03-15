__all__ = ["SVMConfig", "SVM"]

import numpy as np
from typing import override
from dataclasses import dataclass
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ...interface import IDataset
from .classifier import *


@dataclass
class SVMConfig(BinaryClassifierConfig):
    pass

class SVM(BinaryClassifier):
    
    def __init__(self, config: SVMConfig | None = None) -> None:
        super().__init__(config)

        self._name       = "Logistic regression"
        self._config     = config or self.get_default_config()

        self._model      = make_pipeline(StandardScaler(), SVC(gamma='auto', probability=True))
        self._is_trained = False

    @override
    def get_default_config(self) -> SVMConfig:
        return SVMConfig()

    # Predictor
    @override
    def train(self, data: IDataset) -> None:
        target, regressors = self._get_regressors(data)

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

        y_probs = [x[1] for x in self._model.predict_proba(X)]
        y_class = [int(x >= self._config.classification_threshold) for x in y_probs]

        data.set_field_values(self._config.output_prob_field,  y_probs)
        data.set_field_values(self._config.output_class_field, y_class)

        return data

