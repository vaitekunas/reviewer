__all__ = ["DefaultAnalyticsService"]


import json
import logging
from logging import Logger
from typing import Optional, override, Type, TypeVar

from sqlalchemy.orm import Session 

from ..dto import *
from ..dto import MethodRegistrationDTO
from ..interfaces import AnalyticsService
from ..models import WorkflowRepository

from ...framework.interface import IConfig, IMethod
from ...framework.workflow import Workflow
from ...framework.aliases import WorkflowSchema


T = TypeVar("T", bound=IConfig)


class DefaultAnalyticsService(AnalyticsService):
    def __init__(self, 
                 work_dir:        str,
                 method_registry: str,
                 logger: Logger | None = None) -> None:

        if logger:
            self._logger = logger.getChild("analytics")
        else:
            self._logger = logging.getLogger("analytics")

        self._w_repo = WorkflowRepository(workflow_dir = f"{work_dir}/workflows")

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

    # Methods
    @override
    def get_methods(self) -> dict[MethodType, list[MethodRegistrationDTO]]:
        return self._methods.copy()
    
    # Workflows
    def _validate_workflow_dto(self, workflow: WorkflowDTO) -> Workflow:
        try:
            return Workflow.from_schema(WorkflowSchema.from_dict(workflow.to_dict()))
        except Exception as e:
            raise Exception(f"Invalid workflow: {str(e)}")

    @override
    def get_workflows(self, 
                      t:    Session,
                      user: UserDTO) -> list[WorkflowDTO]:

        return self._w_repo.get_workflows(t, user_id = user.user_id)

    @override
    def get_workflow(self, 
                     t:    Session,
                     user: UserDTO, workflow_name: str) -> Optional[WorkflowDTO]:
        
        return self._w_repo.get_workflow(t, 
                                         user_id = user.user_id, 
                                         workflow_name = workflow_name)

    @override
    def register_workflow(self, 
                          t:         Session,
                          user:      UserDTO,
                          workflow:  WorkflowDTO,
                          name:      str | None  = None,
                          overwrite: bool = False) -> None:

        # Validate DTO
        w = self._validate_workflow_dto(workflow) 

        # Validate name
        if name and w.name != name:
           raise Exception("Invalid workflow name")

        # Store in repo
        w_exists = self.get_workflow(t, user, w.get_config().name) is not None

        if w_exists:
            if not overwrite:
               raise Exception("Workflow name already taken")

            path = self._w_repo.modify_workflow(t, 
                                                user_id       = user.user_id, 
                                                workflow_name = w.name, 
                                                workflow      = workflow)

            self._logger.info(f"Modified workflow '{w.name}' (document: '{path}'")
        else:
            path = self._w_repo.add_workflow(t, 
                                            user_id       = user.user_id, 
                                            workflow_name = w.name, 
                                            workflow      = workflow)

            self._logger.info(f"Registered workflow '{w.name}' (document: '{path}'")

    @override
    def unregister_workflow(self, 
                            t:    Session,
                            user: UserDTO,
                            name: str) -> None:
        
        # Find workflow
        w = self.get_workflow(t, user, name)
        if not w:
            raise Exception("Workflow not found")

        # Delete workflow
        self._w_repo.delete_workflow(t, 
                                     user_id       = user.user_id, 
                                     workflow_name = name) 

    # Analysis
    @override
    def get_analysis(self, 
                     t:    Session,
                     user: UserDTO) -> list[AnalysisDTO]:
        raise NotImplementedError()

    @override
    def register_analysis(self, 
                          t:         Session,
                          analysis:  AnalysisDTO,
                          overwrite: bool = False) -> None:
        raise NotImplementedError()


    @override
    def run_analysis(self, analysis: AnalysisDTO) -> ResultsDTO:
        raise NotImplementedError()
