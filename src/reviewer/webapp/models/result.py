"""
Result data models and repository

Is used to persistently store and represent a Result.
For transportation purposes ResultDTO is used.
"""

__all__ = ["ResultRepository"]

import os
import json
import base64
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Integer, String, DateTime, and_, func, true
from sqlalchemy.orm import mapped_column, Session
from typing import Any, Optional

from . import ORM_BASE
from ..interfaces import Repository
from ..dto import RawResultsDTO, ResultType, ResultDTO, ResultsDTO, RunDTO

from reviewer.framework import Figure, Dataset
from reviewer.framework.aliases import AnalysisSchema


class Run(ORM_BASE):
    __tablename__ = "meta_run"

    id         = mapped_column(Integer, primary_key=True)
    user_id    = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    name       = mapped_column(String,  nullable=False)
    created_at = mapped_column(DateTime)

class Result(ORM_BASE):
    __tablename__ = "meta_result"

    id          = mapped_column(Integer, primary_key=True)
    name        = mapped_column(String,  nullable=False)
    result_type = mapped_column(String,  nullable=False)
    workflow_id = mapped_column(String,  nullable=False)
    method_id   = mapped_column(String,  nullable=False)
    filename    = mapped_column(String,  nullable=False)

class Results(ORM_BASE):
    __tablename__ = "meta_results"

    id        = mapped_column(Integer, primary_key=True)
    run_id    = mapped_column(Integer, ForeignKey("meta_run.id"), nullable=False)
    result_id = mapped_column(Integer, ForeignKey("meta_result.id"), nullable=False)


class ResultRepository(Repository):

    def __init__(self, 
                 result_dir: str) -> None:

        super().__init__()

        self._result_dir = result_dir
        os.makedirs(result_dir, exist_ok = True)

    def _get_clean_result_dir(self, user_id: int, run_id: int) -> str:
        return f"{self._result_dir}/{user_id}/{run_id}"

    def _get_clean_result_name(self, user_id: int, run_id: int, name: str) -> str:
        return f"{self._get_clean_result_dir(user_id, run_id)}/{name}"

    def _get_analysis_filepath(self, user_id: int, run_id: int) -> str:
        return self._get_clean_result_name(user_id, run_id, "analysis.json")

    def _store_dataset(self, user_id: int, run_id: int, filename: str, value: Dataset) -> None:

        fullpath = self._get_clean_result_name(user_id, run_id, filename)

        with open(fullpath, "w") as f:
            json.dump(value.to_dict(), f, indent=2)

    def _store_figure(self, user_id: int, run_id: int, filename: str,  value: Figure) -> None:

        fullpath = self._get_clean_result_name(user_id, run_id, filename)

        with open(fullpath, "wb") as f:
            f.write(value.to_bytes())

    def _load_dataset(self, user_id: int, run_id: int, filename: str, decimals: int = 2) -> dict[str, list[Any]]:
        fullpath = self._get_clean_result_name(user_id, run_id, filename)

        with open(fullpath, "r") as f:
            value = {k: [vi if not isinstance(vi, float) else round(vi, decimals) for vi in v] for k, v in json.load(f).items()}

        return value

    def _load_figure(self, user_id: int, run_id: int, filename: str) -> str:
        fullpath = self._get_clean_result_name(user_id, run_id, filename)

        with open(fullpath, "rb") as f:
            value = f.read()

        ext = fullpath.split(".")[-1]

        return f"data:image/{ext};base64," + base64.b64encode(value).decode("ascii")

    def get_run_count(self, 
                      session: Session,
                      user_id: Optional[int]) -> int:

        return (session
                .query(Run)
                .filter(Run.user_id == user_id if user_id else true())
                .count())

    def get_result_count(self, 
                         session: Session,
                         user_id: Optional[int]) -> int:
        return (session
                .query(Result)
                .filter(Result.user_id == user_id if user_id else true())
                .count())

    def get_runs(self,
                 session: Session,
                 user_id: int) -> list[RunDTO]:

        r = (session
                .query(Run) 
                .filter(Run.user_id == user_id)
                .join(Results, Results.run_id == Run.id)
                .with_entities(Run.id, 
                               Run.name,
                               Run.created_at,
                               func.count(func.distinct(Results.result_id)).label("results"))
                .group_by(Run.id)
                .order_by(Run.created_at.desc())
                .all())

        runs = []
        for ri in r:
            try:
                with open(self._get_analysis_filepath(user_id, ri.id), "r") as f:
                    analysis_schema = AnalysisSchema.from_dict(json.load(f))

                runs.append(RunDTO(run_id          = ri.id, 
                                   name            = ri.name,
                                   analysis_schema = analysis_schema,
                                   result_count    = ri.results,
                                   created_at_utc  = ri.created_at))
            except:
                pass

        return runs

    def store_run(self,
                  session:  Session,
                  user_id:  int,
                  name:     str,
                  analysis: AnalysisSchema,
                  results:  RawResultsDTO) -> int:

        # Create database record
        r = Run(user_id = user_id, name = name, created_at = datetime.now(timezone.utc)) 
        session.add(r)
        session.flush()

        # Create directory
        out_dir = self._get_clean_result_dir(user_id, run_id := r.id)
        os.makedirs(out_dir)

        # Store analysis file
        with open(self._get_analysis_filepath(user_id, run_id), "w") as f:
            json.dump(analysis.to_dict(), f, indent=2)

        # Process results
        for workflow_id, workflow_results in results.items():
            for method_id, method_results in workflow_results.items():
                for result in method_results:

                    # Store individual files to disk
                    records = []
                    match result.result_type:

                        case ResultType.DATASET_DICT:
                            for rsubname, rsubvalue in result.value.items():
                                filename = f"{result.result_name}_{rsubname}.json"

                                records.append(Result(name        = f"{result.result_name}/{rsubname}",
                                                      result_type = ResultType.DATASET.value.lower(),
                                                      workflow_id = workflow_id,
                                                      method_id   = method_id,
                                                      filename    = filename))

                                self._store_dataset(user_id, run_id, filename, rsubvalue)

                        case ResultType.DATASET:
                            filename = f"{result.result_name}.json"

                            records.append(Result(name        = result.result_name,
                                                  result_type = ResultType.DATASET.value.lower(),
                                                  workflow_id = workflow_id,
                                                  method_id   = method_id,
                                                  filename    = filename))

                            self._store_dataset(user_id, run_id, filename, result.value)

                        case ResultType.FIGURE:
                            filename = f"{result.result_name}.png"

                            records.append(Result(name        = result.result_name,
                                                  result_type = ResultType.FIGURE.value.lower(),
                                                  workflow_id = workflow_id,
                                                  method_id   = method_id,
                                                  filename    = filename))

                            self._store_figure(user_id, run_id, filename, result.value)

                        case _:
                            raise Exception("Currently unsupported result type")

                    # Create database records
                    for record in records:
                        session.add(record)
                        session.flush()
                        result_map = Results(run_id    = run_id,
                                             result_id = record.id)
                        session.add(result_map)

                    session.flush()

        return run_id

    def delete_run(self,
                   session: Session,
                   user_id: int,
                   run_id:  int) -> None:

        # Check existence and ownership
        r = (session
                .query(Run)
                .filter(Run.id == run_id,
                        Run.user_id == user_id)
                .first())

        if r is None:
            return 

        # run <--> result mapping
        results = (session
                    .query(Results)
                    .filter(Results.run_id == run_id)
                    .all())

        # individual results
        result = (session
                    .query(Result)
                    .join(Results, Results.result_id == Result.id)
                    .filter(Results.run_id == run_id)
                    .all())

        # Delete run <--> result mapping
        for ri in results:
            session.delete(ri)

        # Delete result files
        for ri in result:
            rpath = self._get_clean_result_name(user_id, run_id, ri.filename)

            session.delete(ri)

            # Try deleting the file
            try:
                if os.path.isfile(rpath):
                    os.unlink(rpath)
            except:
                pass

        # Delete run
        dpath = self._get_clean_result_dir(user_id, run_id)
        session.delete(r)

        # Delete analysis file
        if os.path.isfile(analysis_path := self._get_analysis_filepath(user_id, run_id)):
            try:
                os.unlink(analysis_path)
            except:
                pass

        # Try deleting the directory
        try:
            os.rmdir(dpath)
        except:
            pass
                        
        session.flush()

    def get_results(self,
                    session: Session,
                    user_id: int,
                    run_id:  int) -> Optional[ResultsDTO]:

        """
        Returns all of users results for a single run
        """

        ...
        # Check existence and ownership
        r = (session
                .query(Run)
                .filter(Run.id      == run_id,
                        Run.user_id == user_id)
                .first())

        if r is None:
            return None

        # Load analysis file
        with open(self._get_analysis_filepath(user_id, run_id), "r") as f:
            analysis = AnalysisSchema.from_dict(json.load(f))

        # Individual results
        records = (session
                    .query(Result)
                    .join(Results, Results.result_id == Result.id)
                    .filter(Results.run_id == run_id)
                    .all())

        # Build ResultsDTO
        results = {}
        for r in records:

            # Load file value
            if r.result_type == "dataset":
                value = self._load_dataset(user_id, run_id, r.filename)
            elif r.result_type == "figure":
                value = self._load_figure(user_id, run_id, r.filename)
            else:
                continue

            # Add to results
            if (wid := r.workflow_id) not in results:
                results[wid] = {}

            if (mid := r.method_id) not in results[wid]:
                results[wid][mid] = []

            results[wid][mid].append(ResultDTO(result_name = r.name,
                                               result_type = r.result_type.lower(),
                                               value       = value))

        return ResultsDTO(run_id          = run_id,
                          analysis_schema = analysis, 
                          results         = results)


    def get_result_by_name(self,
                           session:     Session,
                           user_id:     int,
                           run_id:      int,
                           result_name: str) -> Optional[ResultDTO]:

        """
        Returns a single result by its name, if it w_exists
        """
        
        # Get record
        result_name = result_name.replace("|", "/")

        record = (session
                    .query(Result)
                    .join(Results, Results.result_id == Result.id)
                    .join(Run, Run.id == Results.run_id)
                    .filter(Run.user_id == user_id,
                            Results.run_id == run_id,
                            func.lower(Result.name) == result_name.strip().lower())
                    .first())

        if record is None:
            return None

        # Load file value
        if record.result_type == "dataset":
            value = self._load_dataset(user_id, run_id, record.filename.replace("/","_"))

        elif record.result_type == "figure":
            value = self._load_figure(user_id, run_id, record.filename.replace("/","_"))

        else:
            return None

        return ResultDTO(result_name = record.name,
                         result_type = record.result_type,
                         value       = value)

