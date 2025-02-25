import polars as pl
from typing import Any
from ....implementations.polars_simple_imputer import PolarsImputer
from ....bases.handler import AHandler


class SimpleImputerWrapperPolars(AHandler):

    def __init__(self, column: str, strategy="most_frequent", fill_value: Any = None) -> None:
        self.column = column
        self.strategy = strategy
        self.fill_value = fill_value
        self.imputer = PolarsImputer(strategy=strategy, fill_value=fill_value)

    def fit(self, df: pl.DataFrame) -> 'SimpleImputerWrapperPolars':
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in the DataFrame.")

        self.imputer.fit(df[self.column])
        return self
    
    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in the DataFrame.")

        # Apply the imputer and update the column
        imputed_column = self.imputer.transform(df[self.column])
        df = df.with_columns(imputed_column.alias(self.column))
        return df
