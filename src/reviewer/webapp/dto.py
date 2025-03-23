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
            "ResultsDTO",
           ]

import importlib
import json
from pandas import DataFrame
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Any, Optional, Type, TypeAlias, TypeVar

from ..framework.interface import IConfig, IMethod


class MethodType(Enum):

    PREPROCESSOR          = "preprocessing"
    EMBEDDER              = "embedding"
    DESCRIPTIVE_STATISTIC = "description"
    TEMPORAL_STATISTIC    = "trend"
    CLASSIFIER            = "classification"
    RECOMMENDER           = "recommendation"
    EVALUATION_METRIC     = "evaluation"
    VISUALIZATION         = "visualization"

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
    ...

@dataclass 
class MethodDTO:
    name:          str
    description:   str
    classname:     str
    config:        dict[str, Any]
    in_workflows:  int = 0
    in_analysis:   int = 0
    total_results: int = 0

@dataclass 
class MethodRegistrationDTO:
    name: str
    description:   str
    method_type:   MethodType
    method_config: Type[IConfig]
    method_class:  Type[IMethod]

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

        method_type   = [x for x in MethodType if x.value == registration["method_type"]][0]

        return MethodRegistrationDTO(name          = registration["name"],
                                     description   = registration["description"],
                                     method_type   = method_type,
                                     method_config = method_config,
                                     method_class  = method_class)

# Foreign IDs
from ..framework.aliases import MethodID, WorkflowID, AnalysisID

# Foreign DTOs
from ..framework.aliases import WorkflowSchema  as WorkflowDTO
from ..framework.aliases import AnalysisSchema  as AnalysisDTO
from ..framework.aliases import AnalysisResults as ResultsDTO


