__all__ = ["WorkflowID", "MethodID",
           "Result", "ResultType", "ResultName", "NamedResults", "WorkFlowResults", "AnalysisResults",
           "DatasetField", "AnalysisField", "AnalysisFieldMappings",
           "StepSchema", "WorkflowSchema", "AnalysisSchema"]

from enum import Enum
from typing import Any, Type, TypeAlias
from dataclasses import asdict, dataclass

WorkflowID:      TypeAlias = str
MethodID:        TypeAlias = str
DatasetField:    TypeAlias = str
AnalysisField:   TypeAlias = str

@dataclass 
class FieldSchema:
    dtype: Type[Any] | Any
    prefix: bool = False
    description: str | None = None

@dataclass
class AnalysisFields:
    required:  dict[AnalysisField, FieldSchema]
    created:   dict[AnalysisField, FieldSchema]
    available: dict[AnalysisField, FieldSchema]

AnalysisFieldMappings: TypeAlias = dict[AnalysisField, DatasetField]

class ResultType(Enum):
    DATASET      = "dataset"
    DATASET_DICT = "dataset_dict"
    FIGURE       = "figure"
    PERCENT      = "percent"
    FLOAT        = "float"
    INTEGER      = "integer"
    STRING       = "string"

@dataclass
class Result:
    method_id:   MethodID
    result_name: str
    result_type: ResultType
    value:       Any

    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return f"Result '{self.result_name}'"

ResultName:      TypeAlias = str
NamedResults:    TypeAlias = dict[ResultName, Result]
WorkFlowResults: TypeAlias = dict[MethodID, list[Result]]
AnalysisResults: TypeAlias = dict[WorkflowID, WorkFlowResults]

@dataclass
class StepSchema:
    id:        str
    module:    str
    classname: str
    config:    dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(step_dict: dict[str, Any]) -> 'StepSchema':
        return StepSchema(id        = step_dict["id"],
                          module    = step_dict["module"],
                          classname = step_dict["classname"],
                          config    = step_dict["config"])

@dataclass
class WorkflowSchema:
    id:     str
    config: dict[str, Any]
    steps:  list[StepSchema]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(workflow_dict: dict[str, Any]) -> 'WorkflowSchema':
        wdict = WorkflowSchema(id     = workflow_dict["id"],
                               config = workflow_dict["config"],
                               steps  = [])

        for sdict in workflow_dict["steps"]:
            wdict.steps.append(StepSchema.from_dict(sdict))

        return wdict

@dataclass
class AnalysisSchema:
    id: str 
    config: dict[str, Any]
    workflows: list[WorkflowSchema]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(analysis_dict: dict[str, Any]) -> 'AnalysisSchema':
        adict = AnalysisSchema(id        = analysis_dict["id"],
                               config    = analysis_dict["config"],
                               workflows = [])

        for wdict in analysis_dict["workflows"]:
            adict.workflows.append(WorkflowSchema.from_dict(wdict))

        return adict


