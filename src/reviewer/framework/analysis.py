__all__ = ["AnalysisConfig", "Analysis"]

from dataclasses import asdict, dataclass
import pickle
from typing import Any

from .interface import IConfig, IDataset, ILogger
from .trait import get_object_id, Identifiable, Configurable
from .workflow import Workflow
from .aliases import ResultType, ResultName, AnalysisResults, FieldSchema, AnalysisFields, AnalysisFieldMappings, WorkflowID
from .aliases import AnalysisSchema

from .runtime import Runtime

@dataclass
class AnalysisConfig(IConfig):

    """

    Attributes: 
        name: name of the analysis
    """

    name: str
    

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Analysis(Identifiable, Configurable[AnalysisConfig]):

    def __init__(self, 
                 config:  AnalysisConfig | None = None) -> None:

        super().__init__()

        self._config = config or self.get_default_config()
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

    def run(self, 
            runtime: Runtime,
            data:    IDataset, 
            mapping: AnalysisFieldMappings,
            logger:  ILogger | None = None) -> tuple[IDataset, AnalysisResults]:

        """Runs an analysis

        Args:
            data: dataset to be used for analysis
            mapping: a map of required fields onto dataset fields
        Returns:
            
        """

        data = data.copy()
        
        # Verify field and perform mapping
        for rfield, schema in self.get_fields().required.items():
            if not rfield.strip():
                continue

            if rfield not in mapping:
                raise Exception(f"Mapping for field '{rfield}' missing")

            rfield_mapped = mapping[rfield]
            fields = [mapping[rfield]] if not schema.prefix else [x for x in data.fields.keys() if x.startswith(rfield_mapped)]

            for field in fields:
                if not data.verify_schema(field, schema.dtype):
                    raise Exception(f"Schema for field '{field}' is wrong: expecting '{schema.dtype}'")

            if not schema.prefix:
                data.map_field(mapping[rfield], rfield)

        # Run analysis
        results: AnalysisResults = {}
        for workflow in self._workflows:
            if logger:
                logger.log(f"Starting workflow '{workflow}'")

            data, result = workflow.run(runtime, data, logger)

            results[workflow.id] = result

        return data, results

    def get_fields(self) -> AnalysisFields:

        required:  dict[str, FieldSchema] = {}
        created:   dict[str, FieldSchema] = {}
        available: dict[str, FieldSchema] = {}
        dropped:   set[str] = set()

        for w in self._workflows:
            fields = w.get_fields()
            
            bad_types = {k for k,v in fields.required.items() if k in required and v.dtype is not Any and required[k].dtype is not Any and v.dtype != required[k].dtype}
            assert not bad_types, f"Some required fields ({', '.join(list(bad_types))}) have mismatching type requirements"
            assert not {k for k in fields.created if k in required or k in created}, "Repeated creation of same field"

            required_new = {k: v for k, v in fields.required.items()
                                if (not v.prefix and k not in created) or
                                   (v.prefix and not any([x.startswith(k) for x in created]))}

            dropped.update({k for k in fields.required if k not in fields.available})
            dropped.update({k for k in fields.created  if k not in fields.available})

            required  = {**required,  **required_new}     # Fields that must be present in the original dataset
            created   = {**created,   **fields.created}   # Fields created (and possibly dropped) by the workflows
            available = {**available, **fields.available} # Fields available after all the workflows complete

        available = {k: v for k,v in available.items() if k not in dropped}

        return AnalysisFields(required = required, created = created, available = available)

    def get_results(self) -> dict[WorkflowID, dict[ResultName, ResultType]]:
        """Returns the name: type dictionaries of reults for each workflow

        Returns:
            
        """
        results = {}

        for w in self._workflows:
            results[w.id] = w.get_results()

        return results

    def to_schema(self) -> AnalysisSchema:
        adict = AnalysisSchema(id        = self.id,
                               config    = self._config.to_dict(),
                               workflows = [])

        for w in self._workflows:
            adict.workflows.append(w.to_schema())

        return adict

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def from_schema(analysis_dict: AnalysisSchema) -> 'Analysis':                    

        try:
            analysis = Analysis(config = AnalysisConfig(**analysis_dict.config))
            analysis._id = analysis_dict.id or get_object_id(analysis)

            for workflow_schema in analysis_dict.workflows:
                analysis.add(Workflow.from_schema(workflow_schema))

        except Exception as e:
            raise Exception(f"Invalid analysis schema: {str(e)}")

        return analysis

    @staticmethod
    def deserialize(serialized: bytes) -> 'Analysis':

        try:
            obj = pickle.loads(serialized)
        except Exception as e:
            raise Exception(f"Could not deserialize pickle file: {str(e)}")

        if not isinstance(obj, Analysis):
            raise Exception("Invalid object class")

        return obj

