"""
Collection of all the Data Transfer Objects used in this application. The DTOs 
are ephemereal data structures used to transport data between the frontend and 
the backend, as well as between the components within the backend.

These objects are not persistent and may be denormalized. The data structures 
used for persistent representation are found in the `models` module.
"""

__all__ = [ "MethodType", 
            "DatasetID", "MethodID", "WorkflowID", "AnalysisID",

            "UserDTO", "SessionTokenDTO",
            "DatasetDTO",
            "MethodRegistrationDTO", "MethodDTO",
            "WorkflowDTO", "AnalysisDTO",

            "AnalysisSchema",
            "AnalysisFieldsDTO",
            "RunSetupDTO",
            "RunDTO",

            "ResultType",
            "RawResultDTO",
            "RawResultsDTO",

            "ResultDTO",
            "ResultsDTO",

            "StatisticsDTO",
           ]

import importlib
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Any, Optional, Type, TypeAlias, TypeVar

from pydantic import BaseModel, model_serializer

from ..framework.interface import IConfig, IMethod

# Foreign IDs
from ..framework.aliases import AnalysisFields, MethodID, ResultName, WorkflowID, AnalysisID

# Foreign DTOs
from ..framework.aliases import Result as RawResultDTO, ResultType
from ..framework.aliases import AnalysisSchema, AnalysisResults as RawResultsDTO


class MethodType(Enum):

    PREPROCESSOR          = "preprocessing"
    EMBEDDER              = "embedding"
    DESCRIPTIVE_STATISTIC = "description"
    TEMPORAL_STATISTIC    = "trend"
    CLASSIFIER            = "classification"
    RECOMMENDER           = "recommendation"
    EVALUATION_METRIC     = "evaluation"
    VISUALIZATION         = "visualization"
    LLM                   = "llm"

# Generics
T = TypeVar("T", bound = IConfig)

# Local IDs
DatasetID: TypeAlias = str

# Local DTOs
@dataclass 
class UserDTO:
    """
    Representation of an application user.
    """
    user_id:       int
    username:      str

@dataclass
class SessionTokenDTO:
    """
    Representation of a session token used to verify user identity and authority.
    """
    user_id:    int
    username:   str
    token:      str
    expires_at: int

@dataclass
class DatasetDTO:
    name:      str
    n_columns: int 
    n_rows:    int
    columns:   list[str]
    data:      Optional[dict[str, list[Any]]] = None

@dataclass 
class MethodRegistrationDTO:
    name: str
    description:     str
    method_type:     MethodType
    method_config:   Type[IConfig]
    method_class:    Type[IMethod]
    required_fields: dict[str, Type[Any] | Any]

    def to_dict(self) -> dict[str, str]:
        return {"name":                    self.name,
                "description":             self.description,
                "method_type":             self.method_type.value,
                "method_config_module":    self.method_config.__module__,
                "method_config_classname": self.method_config.__name__,
                "method_class_module":     self.method_class.__module__,
                "method_class_classname":  self.method_class.__name__}

    @staticmethod
    def from_dict(registration: dict[str, str]) -> 'MethodRegistrationDTO':
        config_module = importlib.import_module(registration["method_config_module"])
        method_config = getattr(config_module, registration["method_config_classname"])

        class_module  = importlib.import_module(registration["method_class_module"])
        method_class  = getattr(class_module, registration["method_class_classname"])
        method        = method_class()

        method_type   = [x for x in MethodType if x.value == registration["method_type"]][0]

        return MethodRegistrationDTO(name            = registration["name"],
                                     description     = registration["description"],
                                     method_type     = method_type,
                                     method_config   = method_config,
                                     method_class    = method_class,
                                     required_fields = method.get_required_fields())

@dataclass 
class MethodDTO:
    name:        str
    description: str
    module:      str
    classname:   str
    method_type: MethodType
    config:      dict[str, Any]
    required:    dict[str, dict[str, Any]]

@dataclass 
class WorkflowDTO:
    config: dict[str, Any]
    steps: list[Any]
    id:    Optional[WorkflowID] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass 
class AnalysisDTO:
    config:    dict[str, Any]
    workflows: list[WorkflowDTO]
    id:        Optional[AnalysisID] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class AnalysisFieldsDTO(BaseModel):
    fields:  AnalysisFields
    results: dict[WorkflowID, dict[ResultName, ResultType]]

    @model_serializer
    def to_dict(self) -> dict[str, Any]:
        fields = {"required":  {k: v.to_dict() for k,v in self.fields.required.items()},
                  "created":   {k: v.to_dict() for k,v in self.fields.created.items()},
                  "available": {k: v.to_dict() for k,v in self.fields.available.items()}}
        results = {k: {ki: vi.value for ki,vi in v.items()} for k,v in self.results.items()}

        return {"fields": fields,
                "results": results}

@dataclass 
class RunSetupDTO:
    dataset_name: str
    mapping:      dict[str, str]
    analysis:     AnalysisDTO

@dataclass 
class RunDTO:
    run_id:          int
    name:            str
    analysis_schema: AnalysisSchema

@dataclass 
class ResultDTO:
    result_name: str
    result_type: str
    value:       bytes | dict[str, list[Any]]

@dataclass 
class ResultsDTO:
    run_id:          int
    analysis_schema: AnalysisSchema
    results:         dict[WorkflowID, dict[MethodID, list[ResultDTO]]]

@dataclass 
class StatisticsDTO:
    datasets:  int
    methods:   int 
    workflows: int 
    analysis:  int
    runs:      int 
    results:   int

