__all__ = ["WorkflowID", "MethodID",
           "Result", "WorkFlowResults", "AnalysisResults",
           "DatasetField", "AnalysisField", "AnalysisFieldMappings"]

from dataclasses import dataclass
from typing import Any, Type, TypeAlias

WorkflowID:      TypeAlias = str
MethodID:        TypeAlias = str
Result:          TypeAlias = Any
WorkFlowResults: TypeAlias = dict[MethodID, list[Result]]
AnalysisResults: TypeAlias = dict[WorkflowID, WorkFlowResults]
DatasetField:    TypeAlias = str
AnalysisField:   TypeAlias = str

@dataclass 
class FieldSchema:
    dtype: Type[Any]
    prefix: bool = False
    description: str | None = None

@dataclass
class AnalysisFields:
    required:  dict[AnalysisField, FieldSchema]
    created:   dict[AnalysisField, FieldSchema]
    available: dict[AnalysisField, FieldSchema]

AnalysisFieldMappings: TypeAlias = dict[AnalysisField, DatasetField]
