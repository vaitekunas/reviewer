__all__ = ["DefaultAnalyticsService"]


import logging
from logging import Logger
from typing import override

from ..dto import *
from ..interfaces import AnalyticsService


class DefaultAnalyticsService(AnalyticsService):
    def __init__(self, 
                 logger: Logger | None = None) -> None:

        if logger:
            self._logger = logger.getChild("analytics")
        else:
            self._logger = logging.getLogger("analytics")

        self._logger.info("AnalyticsService ready")

    @override
    def register_method(self, MethodDTO) -> None:
        ...

    @override
    def get_registered_methods(self) -> list[MethodDTO]:
        ...
    
    @override
    def define_workflow(self, 
                        name: str,
                        description: str, 
                        methods: list[MethodDTO]) -> WorkflowDTO:
        ...

    @override
    def define_analysis(self, 
                        name: str,
                        description: str,
                        workflows: list[WorkflowDTO]) -> AnalysisDTO:
        ...

    @override
    def run_analysis(self, analysis: AnalysisDTO) -> ResultsDTO:
        ...
