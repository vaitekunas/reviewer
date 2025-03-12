__all__ = ["Dataset"]

import pandas as pd
from pandas import DataFrame
from typing import Any, Type, override

from .interface import IDataset


class Dataset(IDataset):

    def __init__(self, df: DataFrame) -> None:
        super().__init__()

        self._df = df

    @override
    def apply_filter(self, sql_rule: str) -> 'Dataset':
        ...

    @override
    def map_column(self, name: str, mapped_name: str) -> 'Dataset':
        ...

    @override
    def verify_schema(self, name: str, dtype: Type[Any]) -> bool:
        ...

    @override
    def drop_columns(self, columns: list[str]) -> 'Dataset':
        ...

    @property
    @override
    def train_data(self) -> 'Dataset':
        ...

    @property
    @override
    def test_data(self) -> 'Dataset':
        ...

    @property
    @override
    def columns(self) -> dict[str, Type[Any]]:
        ...

    @override
    def copy(self) -> 'Dataset':
        ...

    @staticmethod
    def from_path(path: str, sep: str = ";", dec: str = ",") -> 'Dataset':
        df: DataFrame = pd.read_csv(path, sep=sep, decimal=dec)

        return Dataset(df)



