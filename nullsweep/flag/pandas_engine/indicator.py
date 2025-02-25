import pandas as pd
from typing import Optional, Union, Iterable
from ...bases.handler import AHandler


class MissingIndicatorPandas(AHandler):
    """
    A class to generate a binary indicator column for missing values
    in a specified column.
    """

    def __init__(self, column: Optional[Union[Iterable, str]]=None, indicator_column_suffix: str = "_missing"):
        """
        Args:
            column (Optional[Union[Iterable, str]], optional): given column(s) to generate the indicator column for. If None, all columns in the DataFrame will be used. Defaults to None.
            indicator_column_suffix (str, optional): The suffix to append to the column name to generate the indicator column name. Defaults to "_missing".
        """
        if not isinstance(indicator_column_suffix, str):
            raise TypeError("Indicator column suffix must be a string.")
        
        self.column = column
        self.indicator_column_suffix = indicator_column_suffix
        self.indicator_column_names = None

    def fit(self, df: pd.DataFrame) -> 'MissingIndicatorPandas':
        if self.column is None:
            self.column = df.columns.tolist()
        elif isinstance(self.column, str):
            self.column = [self.column] 
        
        # Check if the target column(s) are in the DataFrame
        missing_columns = [col for col in self.column if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Target column(s) {missing_columns} not found in the DataFrame.")

        # Determine the name for the indicator column
        self.indicator_column_names = [
            f"{col}{self.indicator_column_suffix}" for col in self.column
        ]

        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.indicator_column_names is None:
            raise ValueError("The MissingIndicator has not been fitted yet. Call 'fit' first.")

        for col, indicator_name in zip(self.column, self.indicator_column_names):
            df[indicator_name] = df[col].isnull().astype(int)
            
        return df
