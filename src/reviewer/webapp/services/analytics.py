__all__ = ["DefaultAnalyticsService"]


import json
import logging
from logging import Logger
from typing import override, Type, TypeVar 

from ..dto import *
from ..dto import MethodRegistrationDTO
from ..interfaces import AnalyticsService
from ...framework.interface import IConfig, IMethod


T = TypeVar("T", bound=IConfig)


class DefaultAnalyticsService(AnalyticsService):
    def __init__(self, 
                 method_registry: str,
                 logger: Logger | None = None) -> None:

        if logger:
            self._logger = logger.getChild("analytics")
        else:
            self._logger = logging.getLogger("analytics")

        self._methods = {}
        self._register_methods(method_registry)

        self._logger.info("AnalyticsService ready")

    def _register_methods(self, method_registry) -> None:
        with open(method_registry, "r") as f:
            mr = json.load(f)

        for entry in mr:
            registration = MethodRegistrationDTO.from_dict(entry)

            if (mt := registration.method_type) not in self._methods:
                self._methods[mt] = []

            self._methods[mt].append(registration)
            self._logger.info(f"Registering method '{entry['method_class_classname']:<25s}' (type '{mt.value}')")

    @override
    def get_methods(self) -> dict[MethodType, list[MethodRegistrationDTO]]:
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
