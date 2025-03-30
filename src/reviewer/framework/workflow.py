__all__ = ["WorkflowConfig", "Workflow"]

import importlib
from dataclasses import asdict, dataclass
from typing import Any, override, get_args

from .interface import IDataset, IMethod, IConfig, ILogger 
from .interface import IPreprocessor, IEmbedder, IAnalyser, IPredictor, IEvaluator, IVisualizer, IResultCreator
from .trait import get_object_id, Identifiable, Configurable
from .aliases import NamedResults, WorkFlowResults, FieldSchema, AnalysisField, AnalysisFields, Result, ResultType, ResultName
from .aliases import MethodSchema, WorkflowSchema

from .runtime import Runtime


@dataclass
class WorkflowConfig(IConfig):

    """Workflow Configuration

    Attributes: 
        name: name of the Workflow.
        sql_filter: optional sql-like filter rule 
        post_drop_columns: list of columns to drop after the workflow completed.
    """

    name:              str
    sql_filter:        str       | None = None
    post_drop_columns: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """

        Returns:
            
        """
        return asdict(self)

class Workflow(Identifiable, Configurable[WorkflowConfig]):
    """
    Wrapper class for a Pipeline / chain of methods.
    """

    def __init__(self, 
                 config:  WorkflowConfig | None = None,
                 ) -> None:
    
        super().__init__()

        self._config  = config or self.get_default_config()
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

        # Validate step
        _ = self.get_fields()
        _ = self.get_results()

        return self

    def run(self, 
            runtime: Runtime, 
            data:    IDataset,
            logger:  ILogger | None = None) -> tuple[IDataset, WorkFlowResults]:
        """
        Runs through all steps in the workflow and applies them
        on the dataset. A step is allowed to have several roles
        (be an instance of different step types).
        """

        data = data.copy()

        if (filter := self._config.sql_filter):
            data = data.apply_filter(filter)

        results:       WorkFlowResults = {}
        named_results: NamedResults = {}

        def organize_results(step_results: list[Result]) -> None:
            results[mid] += step_results
            named_results.update({r.result_name: r for r in step_results})

        for step in self._steps:
            if logger:
                logger.log(f"Running step '{step.name}'")

            results[mid := step.id] = []

            if isinstance(step, IPreprocessor):
                data = step.preprocess(data)

            if isinstance(step, IEmbedder):
                if not step.is_trained:
                    step.train(data)

                data = step.embed(data)

            if isinstance(step, IAnalyser):
                step_results = step.analyse(data        = data, 
                                            results     = named_results,
                                            new_dataset = runtime.new_dataset)
                organize_results(step_results)

            if isinstance(step, IPredictor):
                if not step.is_trained:
                    step.train(data)

                data = step.predict(data)

            if isinstance(step, IEvaluator):
                step_results = step.evaluate(data, new_dataset = runtime.new_dataset)
                organize_results(step_results)

            if isinstance(step, IVisualizer):
                step_results = step.visualize(data, 
                                              named_results, 
                                              runtime.palette(),
                                              runtime.colormap,
                                              runtime.new_figure)
                organize_results(step_results)

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
                if field in required_fields and field_type.dtype != Any:
                    allowed_types = get_args(old := required_fields[field].dtype) or [old]
                    given_types   = get_args(new := field_type.dtype) or [new]

                    if not set(allowed_types) & set(given_types):
                        raise Exception(f"Incompatible field requirement for '{field}': a previous step requires '{old}', while another requires '{new}'")

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
        required_fields = {k: v for k, v in required_fields.items() if not v.prefix or not any([x.startswith(k) for x in created_fields.keys()])}

        # Available post-run fields
        available_fields = {**required_fields, **created_fields}
        if self._config.post_drop_columns:
            available_fields = {k: v for k, v in available_fields.items() if k not in self._config.post_drop_columns}

        return AnalysisFields(required  = required_fields, 
                              created   = created_fields, 
                              available = available_fields)

    def get_results(self) -> dict[ResultName, ResultType]:
        results = {}

        for step in self._steps:
            if not isinstance(step, IResultCreator):
                continue

            # Validate required results
            for name, rtype in step.get_required_results().items():
                if name not in results:
                    raise Exception(f"Required result '{name}' not available")

                if rtype != results[name]:
                    raise Exception(f"Unexpected result type for '{name}'. Expecting '{rtype}', got '{results[name]}'")

            # Validate created results
            for name, rtype in step.get_created_results().items():
                if name in results:
                    raise Exception(f"Another step creates a result named '{name}'")

                results[name] = rtype

        return results

    def to_schema(self) -> WorkflowSchema:

        wdict = WorkflowSchema(id     = self.id,
                               config = self._config.to_dict(),
                               steps  = [])

        for step in self._steps:
            sdict = step.get_config().to_dict()

            wdict.steps.append(MethodSchema(id        = step.id,
                                            module    = step.__module__,
                                            classname = step.__class__.__name__,
                                            config    = sdict))
        return wdict

    @staticmethod
    def from_schema(workflow_dict: WorkflowSchema) -> 'Workflow':

        try:
            config       = WorkflowConfig(**workflow_dict.config)
            workflow     = Workflow(config)
            workflow._id = workflow_dict.id or get_object_id(workflow)

            for sdict in workflow_dict.steps:

                # Initialize step with default config
                step_module = importlib.import_module(sdict.module)
                step_class = getattr(step_module, sdict.classname)
                step: IMethod[Any] = step_class()

                # Reconfigure step
                step_config = step.get_default_config()
                step_config.update(values = sdict.config)
                step.configure(step_config)
                step._id = sdict.id or get_object_id(step)

                # Add to workflow
                workflow.add(step)
                
        except:
            raise Exception("Could not initialize Workflow")

        return workflow

