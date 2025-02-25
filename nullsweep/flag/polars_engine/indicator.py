import polars as pl
from typing import Optional, Union, Iterable
from ...bases.handler import AHandler


class MissingIndicatorPolars(AHandler):
    """
    A class to generate a binary indicator column for missing values
    in a specified column using Polars DataFrame.
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

    def fit(self, df: pl.DataFrame) -> 'MissingIndicatorPolars':
        """
        Fit the MissingIndicator to the DataFrame.
        
        Args:
            df (pl.DataFrame): The DataFrame to fit the MissingIndicator to.
            
        Returns:
            MissingIndicatorPolars: The fitted MissingIndicator.
        """
        if self.column is None:
            self.column = df.columns
        elif isinstance(self.column, str):
            self.column = [self.column]
        
        # Check if the target column(s) are in the DataFrame
        missing_columns = [col for col in self.column if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Target column(s) {missing_columns} not found in the DataFrame.")

        # Determine the name for the indicator column
        self.indicator_column_names = [
            f"{col}{self.indicator_column_suffix}" for col in self.column
        ]

        return self

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Transform the DataFrame by adding indicator columns for missing values.
        
        Args:
            df (pl.DataFrame): The DataFrame to transform.
            
        Returns:
            pl.DataFrame: The transformed DataFrame with indicator columns.
        """
        if self.indicator_column_names is None:
            raise ValueError("The MissingIndicator has not been fitted yet. Call 'fit' first.")

        # Create expressions for all indicator columns
        expressions = []
        for col, indicator_name in zip(self.column, self.indicator_column_names):
            expressions.append(
                pl.col(col).is_null().cast(pl.Int64).alias(indicator_name)
            )
        
        # Add all indicator columns at once
        return df.with_columns(expressions)