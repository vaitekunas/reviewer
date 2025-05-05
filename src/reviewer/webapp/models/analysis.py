"""
Analysis data models and repository

Is used to persistently store and represent a Analysis.
For transportation purposes AnalysisDTO is used.
"""

__all__ = ["AnalysisRepository"]

import os
import json
from sqlalchemy import ForeignKey, Integer, String, func, true
from sqlalchemy.orm import mapped_column, Session
from typing import Optional

from . import ORM_BASE
from ..interfaces import Repository
from ..dto import AnalysisDTO


class Analysis(ORM_BASE):
    __tablename__ = "meta_analysis"

    id      = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    name    = mapped_column(String,  nullable=False)


class AnalysisRepository(Repository):

    def __init__(self, 
                 analysis_dir: str) -> None:

        super().__init__()

        self._analysis_dir = analysis_dir
        os.makedirs(analysis_dir, exist_ok = True)

    def _get_clean_analysis_name(self, analysis_name: str) -> str:
        return analysis_name.strip().lower().replace(" ","_")

    def get_analysis_count(self, 
                           session: Session,
                           user_id: Optional[int]) -> int:
        return (session
                .query(Analysis)
                .filter(Analysis.user_id == user_id if user_id else true())
                .count())

    def get_analysis(self,
                     session: Session,
                     user_id: int) -> list[AnalysisDTO]:

        """
        Returns all of users analysis
        """

        user_wdir = f"{self._analysis_dir}/{user_id}"

        ws = (session
                .query(Analysis)
                .filter(Analysis.user_id == user_id)
                .order_by(func.lower(Analysis.name))
                .all())

        analysis_list = []
        for w in ws:
            clean_name = self._get_clean_analysis_name(w.name)
            wpath      = f"{user_wdir}/{clean_name}.json"

            if not os.path.isfile(wpath):
                continue

            # Load schema file
            with open(wpath, "r") as f:
                try:
                    analysis = AnalysisDTO(**json.load(f))
                except:
                    continue

            analysis_list.append(analysis)

        return analysis_list

    def get_analysis_by_name(self,
                             session: Session,
                             user_id: int,
                             analysis_name: str) -> Optional[AnalysisDTO]:

        """
        Returns a single analysis by its name, if it w_exists
        """

        user_wdir = f"{self._analysis_dir}/{user_id}"

        w = (session
                .query(Analysis)
                .filter(Analysis.user_id == user_id,
                        func.lower(Analysis.name) == analysis_name.strip().lower())
                .first())

        if w is None:
            return None

        clean_name = self._get_clean_analysis_name(w.name)
        wpath = f"{user_wdir}/{clean_name}.json"
        if not os.path.isfile(wpath):
            return None

        # Load schema file
        with open(wpath, "r") as f:
            try:
                analysis = AnalysisDTO(**json.load(f))
            except:
                return None

        return analysis


    def add_analysis(self, 
                     session:       Session,
                     user_id:       int,
                     analysis_name: str,
                     analysis:      AnalysisDTO) -> str:

        """
        Saves a analysis to the database if no such analysis exists.

        If it exists, an exception is raised.
        """

        # Verify non-existence
        w_exists = (session
                        .query(Analysis)
                        .filter(Analysis.user_id      == user_id,
                                func.lower(Analysis.name) == analysis_name.strip().lower())
                        .first()) is not None

        if w_exists:
            raise Exception("Analysis name exist")

        # Create user dir
        user_wdir = f"{self._analysis_dir}/{user_id}"
        os.makedirs(user_wdir, exist_ok = True)

        # Verify non-existence of the schema-file
        clean_name = self._get_clean_analysis_name(analysis_name)
        wpath = f"{user_wdir}/{clean_name}.json"
        if os.path.isfile(wpath):
            raise Exception("Analysis name exists")

        # Store schema file
        with open(wpath, "w") as f:
            json.dump(analysis.to_dict(), f, indent=2)

        # Create database record
        w = Analysis(user_id = user_id,
                     name    = analysis_name)

        session.add(w)
        session.flush()

        return wpath

    def modify_analysis(self, 
                        session:       Session,
                        user_id:       int,
                        analysis_name: str,
                        analysis:      AnalysisDTO) -> str:

        """
        Modifies an existing analysis by overwriting its schema-file.

        If the database record does not exist, an exception is thrown.
        The non-existence of the schema file does not cause an exception.
        """

        # User's analysis directory
        user_wdir = f"{self._analysis_dir}/{user_id}"

        # Verify existence
        w_exists = (session
                        .query(Analysis)
                        .filter(Analysis.user_id      == user_id,
                                func.lower(Analysis.name) == analysis_name.strip().lower())
                        .first()) is not None

        if not w_exists:
            raise Exception("Analysis does not exist")

        # Validate existence
        clean_name = self._get_clean_analysis_name(analysis_name)
        wpath = f"{user_wdir}/{clean_name}.json"

        # Store json file
        with open(wpath, "w") as f:
            json.dump(analysis.to_dict(), f, indent=2)

        return wpath

    def delete_analysis(self, 
                        session:       Session,
                        user_id:       int,
                        analysis_name: str) -> None:
        """
        Deletes an existing analysis from the database and its
        schema file from the filesystem.

        This method tries to delete the database record and the schema
        file. If one or both do not exist, no exception is thrown.
        """

        # User's analysis directory
        user_wdir = f"{self._analysis_dir}/{user_id}"

        # Verify existence
        w = (session
                .query(Analysis)
                .filter(Analysis.user_id      == user_id,
                        func.lower(Analysis.name) == analysis_name.strip().lower())
                .first())

        # Remove file
        clean_name = self._get_clean_analysis_name(analysis_name)
        wpath      = f"{user_wdir}/{clean_name}.json"

        if os.path.isfile(wpath):
            os.unlink(wpath)

        # Delete database record
        if w is not None:
            session.delete(w)
            session.flush()
