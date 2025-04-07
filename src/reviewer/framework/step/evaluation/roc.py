_all__ = ["ROCConfig", "ROC"]

from dataclasses import asdict, dataclass
from typing import Any, Callable, override
from sklearn.metrics import roc_auc_score, roc_curve

from ...interface import IConfig, IDataset, IEvaluator
from ...aliases import AnalysisField, FieldSchema, Result, ResultName, ResultType


@dataclass
class ROCConfig(IConfig):

    input_field:             str = "y"
    prediction_field_prefix: str = "y_prob"
    output_name:             str = "roc_auc"
    output_curve_data:       str = "roc_curve"

    classification_threshold: float = 0.5

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ROC(IEvaluator[ROCConfig]):

    def __init__(self, config: ROCConfig | None = None) -> None:
        super().__init__(config)

        self._name = "ROC-AUC"    
        self._config = config or self.get_default_config()

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> ROCConfig:
        return ROCConfig()

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
        return {self._config.output_name:  ResultType.DATASET,
                self._config.output_curve_data: ResultType.DATASET_DICT}

    # Evaluator 
    @override
    def evaluate(self, 
                 data: IDataset, 
                 new_dataset: Callable[[dict[str, list[Any]]], IDataset]) -> list[Result]:
        
        cfg = self._config
        data = data.test_data.copy()

        target            = data.get_field_values(cfg.input_field)
        prediction_fields = [x for x in data.fields.keys() if x.startswith(cfg.prediction_field_prefix)]

        fields = {"variable": [],
                  "roc_auc": []}

        curves = {}
        for pf in prediction_fields:
            predictions     = data.get_field_values(pf)

            fields["variable"].append(pf)
            fields["roc_auc"].append(roc_auc_score(target, predictions))

            curve_data = roc_curve(target, predictions)
            curves[pf] = new_dataset({"fpr": curve_data[0].tolist(),
                                      "tpr": curve_data[1].tolist()})


        metrics = [Result(method_id   = self.id,
                          result_name = cfg.output_name,
                          result_type = ResultType.DATASET,
                          value       = new_dataset(fields)),

                   Result(method_id   = self.id,
                          result_name = cfg.output_curve_data,
                          result_type = ResultType.DATASET_DICT,
                          value       = curves)]
        return metrics

