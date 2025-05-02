import dask.dataframe as dd
from typing import Union
from ...bases.handler import AHandler


class ListWiseDeleterDask(AHandler):
    
    def __init__(self, threshold: Union[float, int]=0.5):
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be an integer or a float.")
        
        if isinstance(threshold, float) and not (0 <= threshold <= 1):
            raise ValueError("If threshold is a float, it must be between 0.0 and 1.0.")
        
        if isinstance(threshold, int) and threshold < 0:
            raise ValueError("If threshold is an integer, it must be non-negative.")
        
        self.threshold = threshold
        self.condition: dd.Series = None

    def fit(self, df: dd.DataFrame) -> 'ListWiseDeleterDask':
        num_cols = len(df.columns)
        missing_count = df.isnull().astype(int).sum(axis=1)

        if isinstance(self.threshold, int):
            self.condition = missing_count < self.threshold
        else:
            self.condition = (missing_count / num_cols) < self.threshold
        
        return self
    
    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if self.condition is None:
            raise ValueError("No condition to filter rows. Please fit the handler first.")
        
        return df[self.condition]