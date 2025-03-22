__all__ = ["DefaultAnalyticsService", "MethodType"]


import logging
from logging import Logger
from typing import override, Type, Any

from sqlalchemy import Enum

from ..dto import *
from ..interfaces import AnalyticsService


class DefaultAnalyticsService(AnalyticsService):
    def __init__(self, 
                 logger: Logger | None = None) -> None:

        if logger:
            self._logger = logger.getChild("analytics")
        else:
            self._logger = logging.getLogger("analytics")

        self._methods = {}
        self._logger.info("AnalyticsService ready")

    @override
    def register_method(self, method_type: MethodType, method_class: Type[Any]) -> AnalyticsService:
        if method_type not in self._methods:
            self._methods[method_type] = {}

        classname = method_class.__name__

        self._methods[method_type][classname] = method_class
        self._logger.info(f"Registering method '{classname:<25s}' (type '{method_type.value}')")

        return self

    @override
    def get_registered_methods(self) -> dict[MethodType, dict[str, Type[Any]]]:
        return self._methods.copy()
    
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
