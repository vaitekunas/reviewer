__all__ = ["Dataset"]

import numpy as np
from numpy.dtypes import ObjectDType, Float64DType, Int64DType, BoolDType
import pandas as pd
from pandas import DataFrame 
from typing import Any, Type, override, get_args

from .interface import IDataset


class Dataset(IDataset):

    def __init__(self, df: DataFrame) -> None:
        super().__init__()

        self._df: DataFrame = df.copy()

        self._train_part = 1
        self._train_idx  = []
        self._test_idx   = []

    @override
    def __repr__(self) -> str:
        return str(self._df.head())

    def _has_field(self, field: str) -> bool:
        return field in self._df.columns

    def _match_dtype(self, dtype: Any) -> set[Type[Any] | Any]:

        args = get_args(dtype) or [dtype]

        dtypes = set()
        for arg in args:
        
            if dtype is Any: 
                return set(Any)

            if isinstance(arg, Float64DType) or arg is float:
                dtypes.add(float)

            if isinstance(arg, Int64DType) or arg is int:
                dtypes.add(int)

            if isinstance(arg, BoolDType) or arg is bool:
                dtypes.add(bool)

            if isinstance(arg, ObjectDType) or arg is str:
                dtypes.add(str)

        return dtypes

    @override
    def apply_filter(self, sql_rule: str) -> 'Dataset':

        if self._df is None:
            return self

        self._df = self._df.query(sql_rule).reset_index(drop=True)

        if self._train_idx:
            self._train_idx = [x for x in self._train_idx if x in self._df.index]

        if self._test_idx:
            self._test_idx  = [x for x in self._test_idx if x in self._df.index]

        return self

    @override
    def map_field(self, field: str, mapped_name: str) -> 'Dataset':
        if not self._has_field(mapped_name):
            self._df[mapped_name] = self._df[field]

        return self

    @override
    def verify_schema(self, field: str, dtype: Type[Any] | Any) -> bool:
        if not self._has_field(field):
            return False

        if dtype is Any:
            return True

        required = self._match_dtype(self._df[field].dtype)  
        provided = self._match_dtype(dtype)

        return Any in provided or len(required & provided) > 0

    @override
    def drop_fields(self, fields: list[str]) -> 'Dataset':
        self._df = self._df.drop(columns = fields)

        return self

    @override
    def get_field_values(self, field: str) -> list[Any]:
        if not self._has_field(field):
            return []

        values = self._df[field].tolist()
        if not isinstance(values, list):
            return []

        return values

    @override
    def set_field_values(self, field: str, values: list[Any]) -> None:
        if not len(values) == self._df.shape[0]:
            raise Exception("Cannot set field values - invalid list length")

        self._df[field] = values

    @override
    def partition_train_data(self, train_part: float) -> None:
        if self._train_part != 1:
            return

        if train_part <= 0 or train_part > 1:
            raise Exception("Invalid train_part (expecting value between 0 and 1)")

        self._train_part = train_part
        self._train_idx = np.random.choice(list(self._df.index), 
                                           int(self._df.shape[0] * train_part), 
                                           replace = False)

        self._test_idx = [x for x in self._df.index if x not in self._train_idx]

    @property
    @override
    def train_data(self) -> 'Dataset':
        if not len(self._train_idx):
            return Dataset(self._df.copy())

        return Dataset(self._df.loc[self._train_idx, :].copy().reset_index(drop=True))

    @property
    @override
    def test_data(self) -> 'Dataset':
        if not len(self._test_idx):
            return Dataset(self._df.copy())

        return Dataset(self._df.loc[self._test_idx, :].copy().reset_index(drop=True))

    @property
    @override
    def fields(self) -> dict[str, Type[Any]]:
        return {str(k): self._match_dtype(self._df[k].dtype).pop() for k in self._df.columns}

    @override
    def copy(self) -> 'Dataset':
        new_ds = Dataset(self._df.copy())

        if self._train_part != 1:
            new_ds._train_part = self._train_part
            new_ds._train_idx  = self._train_idx
            new_ds._test_idx   = self._test_idx

        return new_ds

    @override
    def to_dict(self) -> dict[str, list[Any]]:
        return self._df.to_dict("list")

    @staticmethod
    def new(fields: dict[str, list[Any]]) -> 'Dataset':
        df = DataFrame(fields)

        return Dataset(df)

    @staticmethod
    def from_path(path: str, sep: str = ";", dec: str = ",") -> 'Dataset':
        df: DataFrame = pd.read_csv(path, sep=sep, decimal=dec)

        return Dataset(df)


