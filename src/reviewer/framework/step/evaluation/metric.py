__all__ = ["BinaryEvaluationMetricConfig", "BinaryEvaluationMetric"]

from dataclasses import asdict, dataclass
from typing import Any, Callable, override
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from ...interface import IConfig, IDataset, IEvaluator
from ...aliases import AnalysisField, FieldSchema, Result, ResultName, ResultType


@dataclass
class BinaryEvaluationMetricConfig(IConfig):

    input_field:             str = "y"
    prediction_field_prefix: str = "y_prob"
    output_name:             str = "metric"

    do_accuracy:  bool = True
    do_precision: bool = True
    do_recall:    bool = True
    do_f1:        bool = True

    classification_threshold: float = 0.5

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BinaryEvaluationMetric(IEvaluator[BinaryEvaluationMetricConfig]):

    def __init__(self, config: BinaryEvaluationMetricConfig | None = None) -> None:
        super().__init__(config)

        self._name = "Evaluation metric"    
        self._config = config or self.get_default_config()

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return super().name

    # Configurable
    @override
    def get_default_config(self) -> BinaryEvaluationMetricConfig:
        return BinaryEvaluationMetricConfig()

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
        return {self._config.output_name: ResultType.DATASET}

    # Evaluator 
    @override
    def evaluate(self, 
                 data: IDataset, 
                 new_dataset: Callable[[dict[str, list[Any]]], IDataset]) -> list[Result]:
        
        data = data.test_data.copy()
        cfg = self._config

        target            = data.get_field_values(cfg.input_field)
        prediction_fields = [x for x in data.fields.keys() if x.startswith(cfg.prediction_field_prefix)]

        fields = {"variable": []}

        if cfg.do_accuracy:
            fields["accuracy"] = []
        if cfg.do_precision:
            fields["precision"] = []
        if cfg.do_recall:
            fields["recall"] = []
        if cfg.do_f1:
            fields["f1"] = []

        for pf in prediction_fields:
            predictions     = data.get_field_values(pf)
            classifications = [int(x >= cfg.classification_threshold) for x in predictions]

            fields["variable"].append(pf)

            if cfg.do_accuracy:
                fields["accuracy"].append(accuracy_score(target, classifications))

            if cfg.do_precision:
                fields["precision"].append(precision_score(target, classifications, zero_division = 0.0))

            if cfg.do_recall:
                fields["recall"].append(recall_score(target, classifications, zero_division = 0.0))

            if cfg.do_f1:
                fields["f1"].append(f1_score(target, classifications, zero_division = 0.0))

        metrics = [Result(method_id   = self.id,
                          result_name = cfg.output_name,
                          result_type = ResultType.DATASET,
                          value       = new_dataset(fields))]
        return metrics

