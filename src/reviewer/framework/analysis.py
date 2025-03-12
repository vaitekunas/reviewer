__all__ = ["AnalysisConfig", "Analysis"]

from dataclasses import asdict, dataclass
import pickle
from typing import Any

from .interface import IConfig, IDataset, ILogger
from .trait import Identifiable, Configurable
from .workflow import Workflow
from .aliases import AnalysisResults, FieldSchema, AnalysisFields, AnalysisFieldMappings


@dataclass
class AnalysisConfig(IConfig):

    """

    Attributes: 
        name: name of the analysis
    """

    name: str
    

    def get_config_dict(self) -> dict[str, Any]:
        return asdict(self)


class Analysis(Identifiable, Configurable[AnalysisConfig]):

    def __init__(self, 
                 config: AnalysisConfig | None = None,
                 logger: ILogger        | None = None) -> None:

        super().__init__()

        self._config = config or self.get_default_config()
        self._logger = logger
        self._workflows: list[Workflow] = []

    def __repr__(self) -> str:
        return f"{self._config.name} ({self.id})"

    # Identifiable
    @property
    def name(self) -> str:
        return self._config.name

    # Configurable
    def get_default_config(self) -> AnalysisConfig:
        return AnalysisConfig(name = "Default analysis")

    def get_config(self) -> AnalysisConfig:
        return self._config

    def configure(self, config: AnalysisConfig) -> None:
        self._config = config

    # Analysis 
    def add(self, workflow: Workflow) -> 'Analysis':
        self._workflows.append(workflow)

        return self

    def run(self, data: IDataset, mapping: AnalysisFieldMappings) -> AnalysisResults:
        """Runs an analysis

        Args:
            data: dataset to be used for analysis
            mapping: a map of required fields onto dataset fields
        Returns:
            
        """

        data = data.copy()
        
        # Verify field and perform mapping
        for rfield, schema in self.get_fields().required.items():

            if rfield not in mapping:
                raise Exception(f"Mapping for field '{rfield}' missing")

            if not data.verify_schema(rfield, schema.dtype):
                raise Exception(f"Schema for field '{rfield}' is wrong")

            data.map_column(mapping[rfield], rfield)

        # Run analysis
        results: AnalysisResults = {}
        for workflow in self._workflows:
            if self._logger:
                self._logger.log(f"Starting workflow '{workflow}'")

            data, result = workflow.run(data)

            results[workflow.id] = result

        return results

    def get_fields(self) -> AnalysisFields:

        required:  dict[str, FieldSchema] = {}
        created:   dict[str, FieldSchema] = {}
        available: dict[str, FieldSchema] = {}
        dropped:   set[str] = set()

        for w in self._workflows:
            fields = w.get_fields()
            
            assert not {k for k,v in fields.required.items() if k in required and v.dtype != required[k].dtype}, "Some required fields have mismatching type requirements"
            assert not {k for k in fields.created if k in required or k in created}, "Repeated creation of same field"

            required_new = {k: v for k, v in fields.required.items() if k not in created}

            dropped.update({k for k in fields.required if k not in fields.available})
            dropped.update({k for k in fields.created  if k not in fields.available})

            required  = {**required,  **required_new}     # Fields that must be present in the original dataset
            created   = {**created,   **fields.created}   # Fields created (and possibly dropped) by the workflows
            available = {**available, **fields.available} # Fields available after all the workflows complete

        available = {k: v for k,v in available.items() if k not in dropped}

        return AnalysisFields(required = required, created = created, available = available)

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

