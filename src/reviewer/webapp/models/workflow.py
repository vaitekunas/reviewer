__all__ = ["DefaultDocumentStoreService"]

import logging
from logging import Logger
from typing import Optional

from ..dto import *
from ..interfaces import Repository


class DefaultDocumentStoreService(Repository):
    def __init__(self, 
                 logger: Logger | None = None) -> None:

        if logger:
            self._logger = logger.getChild("docstore")
        else:
            self._logger = logging.getLogger("docstore")

        self._logger.info("DocumentStoreService ready")

    # Dataset
    def store_dataset(self, user: UserDTO, workflow: DatasetDTO) -> None:
        raise NotImplementedError()

    def list_datasets(self, user: UserDTO) -> list[DatasetID]:
        raise NotImplementedError()

    def retrieve_dataset(self, user: UserDTO, dataset_id: DatasetID) -> Optional[DatasetDTO]:
        raise NotImplementedError()

    # Workflow
    def store_workflow(self, user: UserDTO, workflow: WorkflowDTO) -> None:
        raise NotImplementedError()

    def list_workflows(self, user: UserDTO) -> list[WorkflowID]:
        raise NotImplementedError()

    def retrieve_workflow(self, user: UserDTO, workflow_id: WorkflowID) -> Optional[WorkflowDTO]:
        raise NotImplementedError()

    # Analysis
    def store_analysis(self, user: UserDTO, workflow: AnalysisDTO) -> None:
        raise NotImplementedError()

    def list_analysis(self, user: UserDTO) -> list[AnalysisID]:
        raise NotImplementedError()

    def retrieve_analysis(self, user: UserDTO, analysis_id: AnalysisID) -> Optional[AnalysisDTO]:
        raise NotImplementedError()
