__all__ = ["DefaultAnalyticsService"]


import json
import logging
from logging import Logger
from typing import Optional, override, TypeVar

from sqlalchemy.orm import Session 

from ..dto import *
from ..interfaces import AnalyticsService
from ..models import WorkflowRepository, DatasetRepository, AnalysisRepository, ResultRepository

from ...framework.interface import IConfig
from ...framework.workflow  import Workflow
from ...framework.analysis  import Analysis
from ...framework.dataset   import Dataset
from ...framework.figure    import Figure
from ...framework.runtime   import Runtime as AnalysisRuntime
from ...framework.aliases   import WorkflowSchema, AnalysisSchema


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
        self._r_repo = ResultRepository(result_dir     = f"{work_dir}/results")

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
    def get_analysis_fields(self, analysis: AnalysisDTO) -> AnalysisFieldsDTO:
        
        analysis_schema = AnalysisSchema.from_dict(analysis.to_dict())
        analyzer        = Analysis.from_schema(analysis_schema)

        return AnalysisFieldsDTO(fields  = analyzer.get_fields(),
                                 results = analyzer.get_results())

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
                     analysis:      AnalysisDTO) -> Optional[RawResultsDTO]:
                     
        # Get data
        data = self.get_dataset_by_name(t, user, dataset_name)
        if data is None or data.data is None:
            return None

        try:
            dataset = Dataset.new(data.data)
        except:
            return None

        # Prepare schema
        analysis_schema    = AnalysisSchema.from_dict(analysis.to_dict())
        analysis_schema.id = None
        for w in analysis_schema.workflows:
            w.id = None
            for s in w.steps:
                s.id = None

        # Prepare analyzer
        analyzer = Analysis.from_schema(analysis_schema)

        analysis_runtime = AnalysisRuntime(dataset_constructor = Dataset.new,
                                           figure_constructor  = Figure.new)

        # Run analysis
        _, results = analyzer.run(runtime = analysis_runtime, 
                                  data    = dataset, 
                                  mapping = mapping)

        # Save results
        self.register_results(t, 
                              user, 
                              name     = analysis_name,
                              analysis = analyzer.to_schema(), 
                              results  = results)

        return results

    # Result 
    @override
    def get_runs(self,
                 t:      Session,
                 user:   UserDTO) -> list[RunDTO]:

        return self._r_repo.get_runs(t, 
                                     user_id = user.user_id)

    @override
    def get_results(self,
                    t:      Session,
                    user:   UserDTO,
                    run_id: int) -> Optional[ResultsDTO]:

        return self._r_repo.get_results(t,
                                        user_id = user.user_id,
                                        run_id  = run_id)

    @override
    def get_result_by_name(self,
                           t:      Session,
                           user:   UserDTO,
                           run_id: int,
                           name :  str) -> Optional[ResultDTO]:

        return self._r_repo.get_result_by_name(t, 
                                               user_id     = user.user_id,
                                               run_id      = run_id,
                                               result_name = name)

    @override
    def register_results(self,
                         t:        Session,
                         user:     UserDTO,
                         name:     str,
                         analysis: AnalysisSchema,
                         results:  RawResultsDTO) -> None:

        self._r_repo.store_run(t, 
                               user_id  = user.user_id, 
                               name     = name,
                               analysis = analysis, 
                               results  = results)

    @override
    def unregister_results(self,
                           t:      Session,
                           user:   UserDTO,
                           run_id: int) -> None:

        self._r_repo.delete_run(t, 
                                user_id = user.user_id, 
                                run_id  = run_id)

