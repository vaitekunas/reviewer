__all__ = ["WorkflowConfig", "Workflow"]

from dataclasses import asdict, dataclass
from typing import Any

from .dataset import Dataset
from .interfaces import Method, Identifiable, Configurable, Config, Logger
from .interfaces import Preprocessor, DataMapper, Embedder, Predictor, Evaluator, Visualizer
from .aliases import WorkFlowResults


@dataclass
class WorkflowConfig(Config):

    name: str
    logger: Logger | None = None

    def get_config_dict(self) -> dict[str, Any]:
        return asdict(self)

    def update(self, values: dict[str, Any]) -> None:
        for k, v in values.items():
            if hasattr(self, k):
                setattr(self, k, v)


class Workflow(Identifiable, Configurable):
    """
    Wrapper class for a Pipeline / chain of methods.
    """

    def __init__(self, config: WorkflowConfig) -> None:
        super().__init__()

        self._config = config
        self._steps: list[Method] = []

    def __repr__(self) -> str:
        return f"{self._config.name} ({self.id})"

    def get_config(self) -> WorkflowConfig:
        return self._config

    def configure(self, config: WorkflowConfig) -> None:
        self._config = config

    def add(self, method: Method)-> 'Workflow':
        """
        Adds a method to the method chain and returns
        self for method chaining.         
        """

        self._steps.append(method)

        return self

    def run(self, data: Dataset) -> WorkFlowResults:
        """
        Runs through all steps in the workflow and applies them
        on the dataset. A step is allowed to have several roles
        (be an instance of different step types).
        """

        data = data.copy()

        results: WorkFlowResults = {}
        for step in self._steps:
            if (logger := self._config.logger):
                logger.log(f"Running step '{step.name}'")

            results[mid := step.id] = []

            if isinstance(step, DataMapper):
                data = step.filter(step.map(data))

            if isinstance(step, Preprocessor):
                data = step.preprocess(data)

            if isinstance(step, Embedder):
                data = step.embed(data)

            if isinstance(step, Predictor):
                if not step.is_trained:
                    step.train(data)

                data = step.predit(data)

            if isinstance(step, Evaluator):
                results[mid].append(step.evaluate(data))

            if isinstance(step, Visualizer):
                results[mid].append(step.visualize(data))

        return (data, results)

    @property
    def name(self) -> str:
        return self._config.name
