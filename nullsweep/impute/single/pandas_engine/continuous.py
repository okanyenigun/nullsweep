import pandas as pd
from sklearn.impute import SimpleImputer
from typing import Any
from ....bases.handler import AHandler


class SimpleImputerWrapper(AHandler):
    """
    A wrapper for sklearn's SimpleImputer to handle single-column imputations.
    """

    def __init__(self, column: str, strategy="most_frequent", fill_value: Any = None) -> None:
        """
        Args:
            column (str): The name of the column to impute.
            strategy (str, optional): The imputation strategy to use. Defaults to "most_frequent". Choices are "mean", "median", "most_frequent", or "constant".
            fill_value (Any, optional): The value to use for imputation when strategy is "constant". Defaults to None.
        """
        if strategy not in {"mean", "median", "most_frequent", "constant"}:
            raise ValueError("Strategy must be one of 'mean', 'median', 'most_frequent', or 'constant'")

        self.column = column
        self.strategy = strategy
        self.fill_value = fill_value
        self.imputer = SimpleImputer(strategy=strategy, fill_value=fill_value)

    def fit(self, df: pd.DataFrame) -> 'SimpleImputerWrapper':
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in the DataFrame.")

        # Reshape the column as SimpleImputer expects 2D input
        self.imputer.fit(df[[self.column]])
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in the DataFrame.")

        # Apply the imputer and update the column
        df[self.column] = self.imputer.transform(df[[self.column]])
        return df
