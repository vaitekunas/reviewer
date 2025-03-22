"""
Collection of all the Data Transfer Objects used in this application. The DTOs 
are ephemereal data structures used to transport data between the frontend and 
the backend, as well as between the components within the backend.

These objects are not persistent and may be denormalized. The data structures 
used for persistent representation are found in the `models` module.
"""

__all__ = [
            "DatasetID", "MethodID", "WorkflowID", "AnalysisID",

            "UserDTO", "SessionTokenDTO",
            "DatasetDTO",
            "MethodDTO",
            "WorkflowDTO", "AnalysisDTO",
            "ResultsDTO",
           ]

import json
from pandas import DataFrame
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Any, Optional, TypeAlias


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
class MethodDTO:
    ...

@dataclass
class DatasetDTO:
    ...

# Foreign IDs
from ..framework.aliases import MethodID, WorkflowID, AnalysisID

# Foreign DTOs
from ..framework.aliases import WorkflowSchema  as WorkflowDTO
from ..framework.aliases import AnalysisSchema  as AnalysisDTO
from ..framework.aliases import AnalysisResults as ResultsDTO


