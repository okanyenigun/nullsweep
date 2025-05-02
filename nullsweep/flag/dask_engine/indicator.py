import dask.dataframe as dd
from typing import Optional, Union, Iterable
from ...bases.handler import AHandler


class MissingIndicatorDask(AHandler):

    def __init__(self, column: Optional[Union[Iterable, str]]=None, indicator_column_suffix: str = "_missing"):
        if not isinstance(indicator_column_suffix, str):
            raise TypeError("Indicator column suffix must be a string.")
        
        self.column = column
        self.indicator_column_suffix = indicator_column_suffix
        self.indicator_column_names = []

    def fit(self, df: dd.DataFrame) -> 'MissingIndicatorDask':
        if self.column is None:
            self.column = list(df.columns)
        elif isinstance(self.column, str):
            self.column = [self.column]

        missing_cols = [col for col in self.column if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Target column(s) {missing_cols} not found in the DataFrame.")
        
        self.indicator_column_names = [f"{col}{self.indicator_column_suffix}" for col in self.column]
        return self
    
    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if not self.indicator_column_names:
            raise ValueError("The MissingIndicator has not been fitted yet. Call 'fit' first.")
        
        assign_kwargs = {
            ind: df[col].isna().astype(int)
            for col, ind in zip(self.column, self.indicator_column_names)
        }

        return df.assign(**assign_kwargs)
    
    def fit_transform(self, df: dd.DataFrame) -> dd.DataFrame:
        return self.fit(df).transform(df)