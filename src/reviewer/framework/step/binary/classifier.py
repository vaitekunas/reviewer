__all__ = ["BinaryClassifierConfig", "BinaryClassifier"]

from dataclasses import asdict, dataclass
from typing import Any, TypeVar, override

from ...interface import IConfig, IDataset, IPredictor
from ...aliases import AnalysisField, FieldSchema

T = TypeVar("T", bound = IConfig)

@dataclass
class BinaryClassifierConfig(IConfig):

    input_field:        str = "y"
    output_prob_field:  str = "y_prob"
    output_class_field: str = "y_pred"
    embedding_prefix:   str = "emb_"
    review_field:       str = "text"
    additional_regressor_fields: list[str] | None = None

    classification_threshold: float = 0.5

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class BinaryClassifier(IPredictor[BinaryClassifierConfig]):

    def __init__(self, 
                 config: BinaryClassifierConfig | None = None) -> None:

        super().__init__(config)

        self._name   = "BinaryClassifier"
        self._config = config or self.get_default_config()
        self._model  = None 
        self._is_trained = False

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable

    @override
    def get_default_config(self) -> BinaryClassifierConfig:
        return BinaryClassifierConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:

        # Obligatory fields
        fields = {self._config.input_field: FieldSchema(dtype = int,  
                                                        description = "Binary target variable (0 or 1)"),

                  self._config.embedding_prefix: FieldSchema(dtype       = int,  
                                                             prefix      = True,
                                                             description = "Prefix for embedding fields"),

                  self._config.review_field: FieldSchema(dtype       = str,  
                                                         description = "Review text")}

        # Optional regressors
        for field in self._config.additional_regressor_fields or []:
            fields[field] = FieldSchema(dtype = float,
                                        description = f"Regressor variable '{field}'")

        return fields

    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.output_prob_field: FieldSchema(dtype = float, 
                                                            description = "Predicted probability score"),

                self._config.output_class_field: FieldSchema(dtype = int, 
                                                             description = "Predicted binary class")}

    # Predictor
    def _get_regressors(self, data: IDataset) -> tuple[list[int], list[list[float]]]:
        cfg = self._config

        target = data.get_field_values(cfg.input_field)
        regressors = []
        for field in list(data.fields.keys()) + (cfg.additional_regressor_fields or []):
            if field.startswith(cfg.embedding_prefix):
                regressors.append(data.get_field_values(field))

        return target, regressors

    @property
    @override
    def is_trained(self) -> bool:
        return self._is_trained
