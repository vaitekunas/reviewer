__all__ = ["ConfusionMatrixConfig", "ConfusionMatrix"]

from dataclasses import asdict, dataclass
from typing import Any, Callable, override
from sklearn.metrics import confusion_matrix

from ...interface import IConfig, IDataset, IEvaluator
from ...aliases import AnalysisField, FieldSchema, Result, ResultName, ResultType


@dataclass
class ConfusionMatrixConfig(IConfig):

    input_field:             str = "y"
    prediction_field_prefix: str = "y_prob"
    output_name_prefix:      str = "confusion_matrix_"

    classification_threshold: float = 0.5

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ConfusionMatrix(IEvaluator[ConfusionMatrixConfig]):

    def __init__(self, config: ConfusionMatrixConfig | None = None) -> None:
        super().__init__(config)

        self._name = "Confusion matrix"    
        self._config = config or self.get_default_config()

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> ConfusionMatrixConfig:
        return ConfusionMatrixConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.input_field: FieldSchema(dtype  = int,
                                                      prefix = False,
                                                      description = "Target variable"),

                self._config.prediction_field_prefix: FieldSchema(dtype = float,
                                                                  prefix = True,
                                                                  description = "Predicted probabilities")}
                                                             
    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {}

    # Result creator 
    @override
    def get_required_results(self) -> dict[ResultName, ResultType]:
        return {}

    @override
    def get_created_results(self) -> dict[ResultName, ResultType]:
        return {self._config.output_name_prefix: ResultType.DATASET}

    # Evaluator 
    @override
    def evaluate(self, 
                 data: IDataset, 
                 new_dataset: Callable[[dict[str, list[Any]]], IDataset]) -> list[Result]:
        
        data = data.test_data.copy()
        cfg  = self._config

        target            = data.get_field_values(cfg.input_field)
        prediction_fields = [x for x in data.fields.keys() if x.startswith(cfg.prediction_field_prefix)]

        results = []
        for pf in prediction_fields:
            predictions     = data.get_field_values(pf)
            classifications = [int(x >= cfg.classification_threshold) for x in predictions]

            cf = confusion_matrix(target, classifications)

            fields = {"real": ["Value 0", "Value 1"],
                      "Predict 0": [cf[0, 0], cf[1, 0]], 
                      "Predict 1": [cf[0, 1], cf[1, 1]]}


            results.append(Result(method_id   = self.id,
                                   result_name = f"{cfg.output_name_prefix}{pf}",
                                   result_type = ResultType.DATASET,
                                   value       = new_dataset(fields)))

        return results

