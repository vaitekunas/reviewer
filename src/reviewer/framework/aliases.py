__all__ = ["WorkflowID", "MethodID",
           "Result", "WorkFlowResults", "AnalysisResults"]

from typing import TypeAlias

from .interfaces import Metric
from .dataset import Dataset
from .figure import Figure

WorkflowID:      TypeAlias = str
MethodID:        TypeAlias = str
Result:          TypeAlias = Dataset | Figure | Metric | float | int
WorkFlowResults: TypeAlias = tuple[Dataset, dict[MethodID, list[Result]]]
AnalysisResults: TypeAlias = dict[WorkflowID, list[WorkFlowResults]]


