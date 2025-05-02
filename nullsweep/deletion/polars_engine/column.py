import polars as pl
from typing import List, Union, Optional
from ...bases.handler import AHandler

class ColumnDeleterPolars(AHandler):
    """
    A class to delete columns from a Polars DataFrame.
    """

    def __init__(self, column: Optional[Union[str, List[str]]] = None):
        self.columns = column
        self.columns_to_delete = None

    def fit(self, df: pl.DataFrame) -> 'ColumnDeleterPolars':
        if self.columns is None:
            # Identify columns with any null values
            self.columns_to_delete = [
                col for col in df.columns if df[col].null_count() > 0
            ]
        else:
            if isinstance(self.columns, str):
                self.columns = [self.columns]
            # Ensure specified columns exist in the DataFrame
            self.columns_to_delete = [col for col in self.columns if col in df.columns]

            if not self.columns_to_delete:
                raise ValueError(
                    f"None of the specified columns {self.columns} exist in the DataFrame."
                )

        return self

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if self.columns_to_delete:
            return df.drop(self.columns_to_delete)
        else:
            raise ValueError(
                "No columns to delete. Please ensure the `fit` method has been called successfully."
            )
