__all__ = ["WorkflowConfig", "Workflow"]

import importlib
from dataclasses import asdict, dataclass
from typing import Any, override


from .interface import IDataset, IMethod, IConfig, ILogger
from .interface import IPreprocessor, IEmbedder, IPredictor, IEvaluator, IVisualizer
from .trait import Identifiable, Configurable
from .aliases import WorkFlowResults, FieldSchema, AnalysisField, AnalysisFields


@dataclass
class WorkflowConfig(IConfig):

    """Workflow Configuration

    Attributes: 
        name: name of the Workflow.
        sql_filter: optional sql-like filter rule 
        post_drop_columns: list of columns to drop after the workflow completed.
        logger: optional logger for announcing step start.
    """

    name:              str
    sql_filter:        str       | None = None
    post_drop_columns: list[str] | None = None

    def get_config_dict(self) -> dict[str, Any]:
        return asdict(self)

class Workflow(Identifiable, Configurable[WorkflowConfig]):
    """
    Wrapper class for a Pipeline / chain of methods.
    """

    def __init__(self, 
                 config: WorkflowConfig | None = None,
                 logger: ILogger | None = None) -> None:
    
        super().__init__()

        self._config = config or self.get_default_config()
        self._logger = logger
        self._steps: list[IMethod[Any]] = []

    def __repr__(self) -> str:
        return f"{self._config.name} ({self.id})"

    # Identifiable
    @property
    @override
    def name(self) -> str:
        return self._config.name

    # Configurable
    @override
    def get_default_config(self) -> WorkflowConfig:
        return WorkflowConfig(name = "Default workflow", post_drop_columns = [])

    @override
    def get_config(self) -> WorkflowConfig:
        return self._config

    @override
    def configure(self, config: WorkflowConfig) -> None:
        self._config = config

    # Workflow methods
    def add(self, method: IMethod[Any])-> 'Workflow':
        """
        Adds a method to the method chain and returns
        self for method chaining.         
        """
        
        self._steps.append(method)

        return self

    def run(self, data: IDataset) -> tuple[IDataset, WorkFlowResults]:
        """
        Runs through all steps in the workflow and applies them
        on the dataset. A step is allowed to have several roles
        (be an instance of different step types).
        """

        data = data.copy()

        if (filter := self._config.sql_filter):
            data = data.apply_filter(filter)

        results: WorkFlowResults = {}
        for step in self._steps:
            if (logger := self._logger):
                logger.log(f"Running step '{step.name}'")

            results[mid := step.id] = []

            if isinstance(step, IPreprocessor):
                data = step.preprocess(data)

            if isinstance(step, IEmbedder):
                data = step.embed(data)

            if isinstance(step, IPredictor):
                if not step.is_trained:
                    step.train(data)

                data = step.predict(data)

            if isinstance(step, IEvaluator):
                results[mid].append(step.evaluate(data))

            if isinstance(step, IVisualizer):
                results[mid].append(step.visualize(data))

        # Drop unnecessary columns
        if (drop_cols := self._config.post_drop_columns):
            data = data.drop_fields(drop_cols)

        return data, results

    def get_fields(self) -> AnalysisFields:

        required_fields: dict[AnalysisField, FieldSchema] = {}
        created_fields:  dict[AnalysisField, FieldSchema] = {}

        for step in self._steps:

            # Required fields
            for field, field_type in step.get_required_fields().items():
                if field in required_fields and field_type.dtype != (old := required_fields[field].dtype):
                    raise Exception(f"Incompatible field requirement for '{field}': a previous step requires '{old}', while another requires '{field_type}'")
                required_fields[field] = field_type

            # Created fields
            for field, field_type in step.get_created_fields().items():

                if field in created_fields:
                    raise Exception(f"Incompatible field creation for '{field}': a previous step created it already.")

                if field in required_fields:
                    raise Exception(f"The created field '{field}' is already required")

                created_fields[field] = field_type

        # Required original fields 
        required_fields = {k: v for k, v in required_fields.items() if k not in created_fields}

        # Available post-run fields
        available_fields = {**required_fields, **created_fields}
        if self._config.post_drop_columns:
            available_fields = {k: v for k, v in available_fields.items() if k not in self._config.post_drop_columns}

        return AnalysisFields(required   = required_fields, 
                              created   = created_fields, 
                              available = available_fields)

    def as_dict(self) -> dict[str, Any]:

        cfg: dict[str, Any] = {"workflow": self._config.get_config_dict(),
                               "steps": []}

        for step in self._steps:
            scfg = step.get_config().get_config_dict()
            cfg["steps"].append({"module": step.__module__,
                                 "class":  step.__class__.__name__,
                                 "config": scfg})

        return cfg

    @staticmethod
    def from_dict(cfg: dict[str, Any]) -> 'Workflow':

        try:
            config   = WorkflowConfig(**cfg["workflow"])
            workflow = Workflow(config)

            for scfg in cfg["steps"]:

                # Initialize step with default config
                step_module = importlib.import_module(scfg["module"])
                step_class = getattr(step_module, scfg["class"])
                step: IMethod[Any] = step_class()

                # Reconfigure step
                step_config = step.get_default_config()
                step_config.update(values = scfg["config"])
                step.configure(step_config)

                # Add to workflow
                workflow.add(step)
                
        except:
            raise Exception("Could not initialize Workflow")

        return workflow

