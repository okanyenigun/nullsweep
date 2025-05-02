import dask.dataframe as dd
from typing import List, Union, Optional
from ...bases.handler import AHandler


class ColumnDeleterDask(AHandler):
    
    def __init__(self, column: Optional[Union[str, List[str]]] = None):
        self.columns = column
        self.columns_to_delete = None

    def fit(self, df: dd.DataFrame) -> 'ColumnDeleterDask':
        if self.columns is None:
            null_counts = df.isnull().sum().compute()
            self.columns_to_delete = null_counts[null_counts > 0].index.tolist()
        else:
            if isinstance(self.columns, str):
                cols = [self.columns]
            else:
                cols = self.columns

            existing = [col for col in cols if col in df.columns]

            if not existing:
                raise ValueError(
                    f"None of the specified columns {self.columns} exist in the DataFrame."
                )
            
            self.columns_to_delete = existing

        return self
    
    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if not self.columns_to_delete:
            raise ValueError(
                "No columns to delete. Ensure `fit` has been called and columns to delete were identified."
            )
        # Return a lazy Dask DataFrame with specified columns dropped
        return df.drop(columns=self.columns_to_delete)