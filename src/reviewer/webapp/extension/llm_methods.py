__all__ = ["LLMPredictorConfig", "LLMPredictor"]

import ollama
from pydantic import BaseModel, create_model
from dataclasses import dataclass, asdict
from typing import Type, override, Any

from .. import runtime

from reviewer.framework.interface import IConfig, IDataset, IPredictor
from reviewer.framework.aliases import AnalysisField, FieldSchema


@dataclass
class LLMPredictorConfig(IConfig):

    input_field:        str = "y"
    output_prob_field:  str = "y_prob"
    output_class_field: str = "y_pred"
    review_field:       str = "text"

    llm_model: str = "gemma2"
    prompt: str    = "Estimate the binary sentiment for the following text; give a sentiment probability (from 0.0 for very negative sentiment to 1.0 for very positive sentiment) and the sentiment class (0 for negative sentiment and 1 for positive sentiment). Your response must be a valid JSON object."

    @override
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class LLMPredictor(IPredictor[LLMPredictorConfig]):

    def __init__(self, config: LLMPredictorConfig | None = None) -> None:
        super().__init__(config)

        self._name       = "Large Language Model"
        self._config     = config or self.get_default_config()

        self._classes    = []
        self._is_trained = False

    def _create_prediction_datamodel(self) -> Type[BaseModel]:

        col_prob = self._config.output_prob_field
        col_pred = self._config.output_class_field

        BinarySentimentPrediction = create_model(
            "BinarySentimentPrediction",
            **{
                col_prob: (float, ...),
                col_pred: (int, ...)
            }
        )

        return BinarySentimentPrediction
    
    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._name

    # Configurable
    @override
    def get_default_config(self) -> LLMPredictorConfig:
        return LLMPredictorConfig()

    # Method
    @override
    def get_required_fields(self) -> dict[AnalysisField, FieldSchema]:

        fields = {self._config.review_field: FieldSchema(dtype       = str,  
                                                         description = "Review text")}
        return fields

    @override
    def get_created_fields(self) -> dict[AnalysisField, FieldSchema]:
        return {self._config.output_prob_field: FieldSchema(dtype = float, 
                                                            description = "Predicted probability score"),

                self._config.output_class_field: FieldSchema(dtype = int, 
                                                             description = "Predicted binary class")}

    # Predictor
    @property
    @override
    def is_trained(self) -> bool:
        return self._is_trained

    @override
    def train(self, data: IDataset) -> None:
        if self.is_trained:
            return

        self._is_trained = True
        self._classes = sorted(list(set(data.get_field_values(self._config.input_field))))

    @override
    def predict(self, data: IDataset) -> IDataset:
        assert self._is_trained, "Model is has not been trained"

        data = data.copy()

        # Setup ollama
        text_prompt = lambda text: f"""{self._config.prompt}

                                       {text}"""

        dm = self._create_prediction_datamodel()
        client = ollama.Client(host = runtime.llm_host)

        # Create predictions
        y_probs = []
        y_class = []
        texts = data.get_field_values(self._config.review_field)
        for text in texts:
            prompt   = text_prompt(text)
            response = client.chat(messages = [
                                {
                                  'role':    'user',
                                  'content': prompt,
                                }
                              ],
                              model  = self._config.llm_model,
                              format = dm.model_json_schema())
            try:
                assert response.message.content is not None
                pred = dm.model_validate_json(response.message.content).model_dump()

                yhat_prob  = pred.get(self._config.output_prob_field, 0.0)
                yhat_class = pred.get(self._config.output_class_field, self._classes[0])

                y_probs.append(yhat_prob)
                y_class.append(yhat_class)
            except:
                y_probs.append(0.0)
                y_class.append(self._classes[0])

        data.set_field_values(self._config.output_prob_field,  y_probs)
        data.set_field_values(self._config.output_class_field, y_class)

        return data

