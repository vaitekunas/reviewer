"""
Workflow data models and repository

Is used to persistently store and represent a Workflow.
For transportation purposes WorkflowDTO is used.
"""

__all__ = ["WorkflowRepository"]

import os
import json
from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.orm import mapped_column, Session
from typing import Optional

from . import ORM_BASE
from ..interfaces import Repository
from ..dto import WorkflowDTO


class Workflow(ORM_BASE):
    __tablename__ = "meta_workflow"

    id      = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    name    = mapped_column(String,  nullable=False)


class WorkflowRepository(Repository):

    def __init__(self, 
                 workflow_dir: str) -> None:

        super().__init__()

        self._workflow_dir = workflow_dir
        os.makedirs(workflow_dir, exist_ok = True)

    def _get_clean_workflow_name(self, workflow_name: str) -> str:
        return workflow_name.strip().lower().replace(" ","_")

    def get_workflows(self,
                      session: Session,
                      user_id: int) -> list[WorkflowDTO]:

        """
        Returns all of users workflows
        """

        user_wdir = f"{self._workflow_dir}/{user_id}"

        ws = (session
                .query(Workflow)
                .filter(Workflow.user_id == user_id)
                .all())

        workflows = []
        for w in ws:
            clean_name = self._get_clean_workflow_name(w.name)
            wpath      = f"{user_wdir}/{clean_name}.json"

            if not os.path.isfile(wpath):
                continue

            # Load schema file
            with open(wpath, "r") as f:
                try:
                    workflow = WorkflowDTO(**json.load(f))
                except:
                    continue

            workflows.append(workflow)

        return workflows

    def get_workflow(self,
                     session: Session,
                     user_id: int,
                     workflow_name: str) -> Optional[WorkflowDTO]:

        """
        Returns a single workflow by its name, if it w_exists
        """

        user_wdir = f"{self._workflow_dir}/{user_id}"

        w = (session
                .query(Workflow)
                .filter(Workflow.user_id == user_id,
                        func.lower(Workflow.name) == workflow_name.strip().lower())
                .first())

        if w is None:
            return None

        clean_name = self._get_clean_workflow_name(w.name)
        wpath = f"{user_wdir}/{clean_name}.json"
        if not os.path.isfile(wpath):
            return None

        # Load schema file
        with open(wpath, "r") as f:
            try:
                workflow = WorkflowDTO(**json.load(f))
            except:
                return None

        return workflow


    def add_workflow(self, 
                     session:       Session,
                     user_id:       int,
                     workflow_name: str,
                     workflow:      WorkflowDTO) -> str:

        """
        Saves a workflow to the database if no such workflow exists.

        If it exists, an exception is raised.
        """

        # Verify non-existence
        w_exists = (session
                        .query(Workflow)
                        .filter(Workflow.user_id      == user_id,
                                func.lower(Workflow.name) == workflow_name.strip().lower())
                        .first()) is not None

        if w_exists:
            raise Exception("Workflow name exist")

        # Create user dir
        user_wdir = f"{self._workflow_dir}/{user_id}"
        os.makedirs(user_wdir, exist_ok = True)

        # Verify non-existence of the schema-file
        clean_name = self._get_clean_workflow_name(workflow_name)
        wpath = f"{user_wdir}/{clean_name}.json"
        if os.path.isfile(wpath):
            raise Exception("Workflow name exists")

        # Store schema file
        with open(wpath, "w") as f:
            json.dump(workflow.to_dict(), f, indent=2)

        # Create database record
        w = Workflow(user_id = user_id,
                     name    = workflow_name)

        session.add(w)
        session.flush()

        return wpath

    def modify_workflow(self, 
                        session:       Session,
                        user_id:       int,
                        workflow_name: str,
                        workflow:      WorkflowDTO) -> str:

        """
        Modifies an existing workflow by overwriting its schema-file.

        If the database record does not exist, an exception is thrown.
        The non-existence of the schema file does not cause an exception.
        """

        # User's workflow directory
        user_wdir = f"{self._workflow_dir}/{user_id}"

        # Verify existence
        w_exists = (session
                        .query(Workflow)
                        .filter(Workflow.user_id      == user_id,
                                func.lower(Workflow.name) == workflow_name.strip().lower())
                        .first()) is not None

        if not w_exists:
            raise Exception("Workflow does not exist")

        # Validate existence
        clean_name = self._get_clean_workflow_name(workflow_name)
        wpath = f"{user_wdir}/{clean_name}.json"

        # Store json file
        with open(wpath, "w") as f:
            json.dump(workflow.to_dict(), f, indent=2)

        return wpath

    def delete_workflow(self, 
                        session:       Session,
                        user_id:       int,
                        workflow_name: str) -> None:
        """
        Deletes an existing workflow from the database and its
        schema file from the filesystem.

        This method tries to delete the database record and the schema
        file. If one or both do not exist, no exception is thrown.
        """

        # User's workflow directory
        user_wdir = f"{self._workflow_dir}/{user_id}"

        # Verify existence
        w = (session
                .query(Workflow)
                .filter(Workflow.user_id      == user_id,
                        func.lower(Workflow.name) == workflow_name.strip().lower())
                .first())

        # Remove file
        clean_name = self._get_clean_workflow_name(workflow_name)
        wpath      = f"{user_wdir}/{clean_name}.json"

        if os.path.isfile(wpath):
            os.unlink(wpath)

        # Delete database record
        if w is not None:
            session.delete(w)
            session.flush()
