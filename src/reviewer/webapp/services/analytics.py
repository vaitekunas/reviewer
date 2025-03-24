__all__ = ["DefaultAnalyticsService"]


import json
import logging
from logging import Logger
from typing import Optional, override, TypeVar

from sqlalchemy.orm import Session 

from ..dto import *
from ..dto import MethodRegistrationDTO
from ..interfaces import AnalyticsService
from ..models import WorkflowRepository, DatasetRepository, AnalysisRepository

from ...framework.interface import IConfig
from ...framework.workflow import Workflow
from ...framework.analysis import Analysis
from ...framework.dataset import Dataset
from ...framework.runtime import Runtime as AnalysisRuntime
from ...framework.aliases import WorkflowSchema, AnalysisSchema


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
        self._a_repo = AnalysisRepository(analysis_dir = f"{work_dir}/analysis")
        self._d_repo = DatasetRepository(data_dir      = f"{work_dir}/datasets")

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
    def get_workflow_by_name(self, 
                             t:    Session,
                             user: UserDTO, workflow_name: str) -> Optional[WorkflowDTO]:
        
        return self._w_repo.get_workflow_by_name(t, 
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
        if name and w.name.lower() != name.lower():
           raise Exception("Invalid workflow name")

        # Store in repo
        w_exists = self.get_workflow_by_name(t, user, w.get_config().name) is not None

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
        w = self.get_workflow_by_name(t, user, name)
        if not w:
            raise Exception("Workflow not found")

        # Delete workflow
        self._w_repo.delete_workflow(t, 
                                     user_id       = user.user_id, 
                                     workflow_name = name) 

    # Dataset 
    @override
    def get_datasets(self, t: Session, user: UserDTO) -> list[DatasetDTO]:
        return self._d_repo.get_datasets(t, user.user_id)

    @override
    def get_dataset_by_name(self, 
                            t: Session, 
                            user: UserDTO, 
                            dataset_name: str) -> Optional[DatasetDTO]:
        return self._d_repo.get_dataset_by_name(t, user.user_id, dataset_name)

    @override
    def register_dataset(self,                               
                         t:         Session,
                         user:      UserDTO,
                         dataset:   DatasetDTO,
                         name:      str,
                         overwrite: bool = False) -> None:

        # Validate name
        if dataset.name.lower() != name.lower():
           raise Exception("Invalid dataset name")

        # Store in repo
        d_exists = self.get_dataset_by_name(t, user, dataset.name) is not None

        if d_exists:
            if not overwrite:
               raise Exception("Dataset name already taken")

            self._d_repo.modify_dataset(t, user.user_id, name, dataset)
        else:
            self._d_repo.add_dataset(t, user.user_id, dataset)

    @override
    def unregister_dataset(self,                               
                           t:    Session,
                           user: UserDTO,
                           name: str) -> None:

        # Find dataset
        d = self.get_dataset_by_name(t, user, name)
        if not d:
            raise Exception("Dataset not found")

        # Delete dataset
        self._d_repo.delete_dataset(t, user.user_id, name)

    # Analysis
    def _validate_analysis_dto(self, analysis: AnalysisDTO) -> Analysis:
        try:
            return Analysis.from_schema(AnalysisSchema.from_dict(analysis.to_dict()))
        except Exception as e:
            raise Exception(f"Invalid analysis: {str(e)}")

    @override
    def get_analysis(self, 
                     t:    Session,
                     user: UserDTO) -> list[AnalysisDTO]:
        
        return self._a_repo.get_analysis(t, user.user_id)

    @override
    def get_analysis_by_name(self, 
                             t:             Session,
                             user:          UserDTO,
                             analysis_name: str) -> Optional[AnalysisDTO]:

        return self._a_repo.get_analysis_by_name(t, user.user_id, analysis_name)

    @override
    def register_analysis(self, 
                          t:         Session,
                          user:      UserDTO,
                          analysis:  AnalysisDTO,
                          name:      str | None  = None,
                          overwrite: bool = False) -> None:

        # Validate DTO
        a = self._validate_analysis_dto(analysis) 

        # Validate name
        if name and a.name.lower() != name.lower():
           raise Exception("Invalid analysis name")

        # Store in repo
        a_exists = self.get_analysis_by_name(t, user, a.get_config().name) is not None

        if a_exists:
            if not overwrite:
               raise Exception("Workflow name already taken")

            path = self._a_repo.modify_analysis(t, 
                                                user_id       = user.user_id, 
                                                analysis_name = a.name, 
                                                analysis      = analysis)

            self._logger.info(f"Modified analysis '{a.name}' (document: '{path}'")
        else:
            path = self._a_repo.add_analysis(t, 
                                             user_id       = user.user_id, 
                                             analysis_name = a.name, 
                                             analysis      = analysis)

            self._logger.info(f"Registered analysis '{a.name}' (document: '{path}'")

    @override
    def unregister_analysis(self, 
                            t:    Session,
                            user: UserDTO,
                            name: str) -> None:

        # Find analysis
        a = self.get_analysis_by_name(t, user, name)
        if not a:
            raise Exception("Analysis not found")

        # Delete analysis
        self._a_repo.delete_analysis(t, 
                                     user_id       = user.user_id, 
                                     analysis_name = name) 

    @override
    def run_analysis(self, 
                     t:             Session,
                     user:          UserDTO,
                     analysis_name: str,
                     dataset_name:  str,
                     mapping:       dict[str, str],
                     analysis:      AnalysisDTO) -> ResultsDTO:
                     
        # Initialize data
        data = Dataset.new(fields = {})

        # Prepare analyzer
        analyzer = Analysis.from_schema(AnalysisSchema.from_dict(analysis.to_dict()))

        analysis_runtime = AnalysisRuntime(dataset_constructor = Dataset.new)
        data_post, results = analyzer.run(runtime = analysis_runtime, 
                                          data    = data, 
                                          mapping = mapping)

        # @TODO: implement result saving using result repository
        # @TODO: also save the analysis.json used to run it.

        return results

        
