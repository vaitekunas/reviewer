"""
Dataset data model and repository

Is used to persistently store and represent a Dataset.
For transportation purposes DatasetDTO is used.
"""
__all__ = ["DatasetRepository"]

import os
import pandas as pd
from pandas import DataFrame
from sqlalchemy import ForeignKey, Integer, String, func, true
from sqlalchemy.orm import mapped_column, Session
from typing import Optional

from . import ORM_BASE
from ..interfaces import Repository
from ..dto import DatasetDTO


class Dataset(ORM_BASE):
    __tablename__ = "meta_dataset"

    id        = mapped_column(Integer, primary_key=True)
    user_id   = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    name      = mapped_column(String,  nullable=False)
    n_rows    = mapped_column(Integer, nullable=False)
    n_columns = mapped_column(Integer, nullable=False)
    columns   = mapped_column(String,  nullable=False)


class DatasetRepository(Repository):

    def __init__(self, 
                 data_dir: str) -> None:

        super().__init__()

        self._data_dir = data_dir
        os.makedirs(data_dir, exist_ok = True)

    def _get_clean_dataset_name(self, dataset_name: str) -> str:
        return dataset_name.strip().lower().replace(" ","_")

    def get_dataset_count(self, session: Session, user_id: Optional[int]) -> int:
        return (session
                .query(Dataset)
                .filter(Dataset.user_id == user_id if user_id else true())
                .count())

    def get_datasets(self,
                     session: Session,
                     user_id: int) -> list[DatasetDTO]:

        """
        Returns all of user's datasets
        """

        user_ddir = f"{self._data_dir}/{user_id}"
        
        ds = (session
                .query(Dataset)
                .filter(Dataset.user_id == user_id)
                .order_by(func.lower(Dataset.name))
                .all())

        datasets = []
        for d in ds:

            # Skip if file does not exist
            clean_name = self._get_clean_dataset_name(d.name)
            dpath = f"{user_ddir}/{clean_name}.csv"
            if not os.path.isfile(dpath):
                continue

            # Add DTO without data
            datasets.append(DatasetDTO(name      = d.name,
                                       n_rows    = d.n_rows,
                                       n_columns = d.n_columns,
                                       columns   = d.columns,
                                       data      = None))

        return datasets

    def get_dataset_by_name(self,
                            session:      Session,
                            user_id:      int,
                            dataset_name: str,
                            with_data:    bool = True) -> Optional[DatasetDTO]:

        """
        Returns a single dataset by its name, if it exists
        """

        user_ddir = f"{self._data_dir}/{user_id}"

        # Check data record existence
        d = (session
             .query(Dataset)
             .filter(Dataset.user_id == user_id,
                     func.lower(Dataset.name) == dataset_name.strip().lower())
             .first())

        if d is None:
            return None

        # Check file existence
        clean_name = self._get_clean_dataset_name(d.name)
        dpath = f"{user_ddir}/{clean_name}.csv"
        if not os.path.isfile(dpath):
            return None

        # Load csv file
        if with_data:
            df = pd.read_csv(dpath, sep=";", decimal=",", encoding="utf-8").head(10)
            data = df.to_dict("list")
        else:
            data = None

        # Create DTO with data
        dataset = DatasetDTO(name      = d.name,
                             n_rows    = d.n_rows,
                             n_columns = d.n_columns,
                             columns   = d.columns.split(","),
                             data      = data)

        return dataset

    def add_dataset(self, 
                    session: Session,
                    user_id: int,
                    dataset: DatasetDTO) -> str:

        """
        Creates a dataset record and stores the data to disk as a CSV file
        """

        user_ddir = f"{self._data_dir}/{user_id}"

        # Dataset must have data
        if dataset.data is None:
            raise Exception("Dataset data missing")

        # Verify non-existence
        d_exists = (session
                        .query(Dataset)
                        .filter(Dataset.user_id == user_id,
                                func.lower(Dataset.name) == dataset.name.strip().lower())
                        .first()) is not None

        if d_exists:
            raise Exception("Dataset name exists!")

        # Create user dir
        os.makedirs(user_ddir, exist_ok = True)

        # Verify non-existence of the schema-file
        clean_name = self._get_clean_dataset_name(dataset.name)
        dpath = f"{user_ddir}/{clean_name}.csv"
        if os.path.isfile(dpath):
            raise Exception("Dataset file exists")

        # Store CSV file
        df = DataFrame(dataset.data)
        df.to_csv(dpath, sep=";", decimal=",", index=False)

        # Create database record
        d = Dataset(user_id   = user_id,
                    name      = dataset.name,
                    columns   = ",".join([str(x) for x in df.columns]),
                    n_rows    = df.shape[0],
                    n_columns = df.shape[1])

        session.add(d)
        session.flush()

        return dpath

    def modify_dataset(self, 
                       session:      Session,
                       user_id:      int,
                       dataset_name: str,
                       dataset:      DatasetDTO) -> str:

        """
        Modifies an existing dataset by overwriting its csv-file
        and modifying the database record.

        If the database record does not exist, an exception is thrown.
        The non-existence of the csv file does not cause an exception.
        """

        user_ddir = f"{self._data_dir}/{user_id}"

        # Check existence
        d = (session
                .query(Dataset)
                .filter(Dataset.user_id == user_id,
                        func.lower(Dataset.name) == dataset_name.strip().lower())
                .first()) 
         
        if d is None:
            raise Exception("Dataset does not exist")

        # Store CSV file
        clean_name = self._get_clean_dataset_name(dataset_name)
        dpath      = f"{user_ddir}/{clean_name}.csv"

        df = DataFrame(dataset.data)
        df.to_csv(dpath, sep=";", decimal=",", index=False)

        # Update data record
        d.n_rows    = df.shape[0]
        d.n_columns = df.shape[1]
        d.columns   = ",".join([str(x) for x in df.columns])
        
        session.flush()

        return dpath

    def delete_dataset(self, 
                       session:      Session,
                       user_id:      int,
                       dataset_name: str) -> None:
        """
        Deletes an existing dataset from the database and its
        csv file from the filesystem.

        This method tries to delete the database record and the schema
        file. If one or both do not exist, no exception is thrown.
        """

        user_ddir = f"{self._data_dir}/{user_id}"

        # Delete CSV file
        clean_name = self._get_clean_dataset_name(dataset_name)
        dpath      = f"{user_ddir}/{clean_name}.csv"

        if os.path.isfile(dpath):
            os.unlink(dpath)

        # Delete database record
        d = (session
                .query(Dataset)
                .filter(Dataset.user_id == user_id,
                        func.lower(Dataset.name) == dataset_name.strip().lower())
                .first()) 
         
        if d is not None:
            session.delete(d)
            session.flush()

