__all__ = ["AnalysisConfig", "Analysis"]

from dataclasses import asdict, dataclass
import pickle
from typing import Any

from .interfaces import Identifiable, Configurable, Config, Logger
from .dataset import Dataset
from .workflow import Workflow

from .aliases import AnalysisResults


@dataclass
class AnalysisConfig(Config):

    name: str
    logger: Logger | None = None

    def get_config_dict(self) -> dict[str, Any]:
        return asdict(self)

    def update(self, values: dict[str, Any]) -> None:
        for k, v in values.items():
            if hasattr(self, k):
                setattr(self, k, v)


class Analysis(Identifiable, Configurable):

    def __init__(self, config: AnalysisConfig) -> None:
        super().__init__()

        self._config = config
        self._workflows = []

    def __repr__(self) -> str:
        return f"{self._config.name} ({self.id})"

    def get_config(self) -> AnalysisConfig:
        return self._config

    def configure(self, config: AnalysisConfig) -> None:
        self._config = config

    def add(self, workflow: Workflow) -> 'Analysis':
        self._workflows.append(workflow)

        return self

    def run(self, data: Dataset) -> AnalysisResults:
        data = data.copy()

        results: AnalysisResults = {}
        for workflow in self._workflows:
            if (logger := self._config.logger):
                logger.log(f"Starting workflow '{workflow}'")

            results[workflow.id] = workflow.run(data)

        return results

    @property
    def name(self) -> str:
        return self._config.name

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def deserialize(serialized: bytes) -> 'Analysis':

        try:
            obj = pickle.loads(serialized)
        except Exception as e:
            raise Exception(f"Could not deserialize pickle file: {str(e)}")

        if not isinstance(obj, Analysis):
            raise Exception("Invalid object class")

        return obj

