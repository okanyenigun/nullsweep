import pandas as pd
from typing import List, Union, Optional
from ..bases.handler import AHandler


class ColumnDeleter(AHandler):
    """
    A class to delete columns from a DataFrame.
    """

    def __init__(self, column: Optional[Union[str, List[str]]]=None):
        self.columns = column
        self.columns_to_delete = None

    def fit(self, df: pd.DataFrame) -> 'ColumnDeleter':
        if self.columns is None:
            self.columns_to_delete = df.columns[df.isnull().any()].tolist()
        else:
            if isinstance(self.columns, str):
                self.columns = [self.columns]
            self.columns_to_delete = [col for col in self.columns if col in df.columns]

            if not self.columns_to_delete:
                raise ValueError(
                    f"None of the specified columns {self.columns} exist in the DataFrame."
                )
        
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.columns_to_delete:
            return df.drop(columns=self.columns_to_delete)
        else:
            raise ValueError(
                "No columns to delete. Please ensure the `fit` method has been called successfully."
            )
    