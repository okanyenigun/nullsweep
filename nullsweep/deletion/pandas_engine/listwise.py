import pandas as pd
from typing import Union
from ...bases.handler import AHandler


class ListWiseDeleterPandas(AHandler):
    """
    A class to delete rows from a DataFrame based on the number of missing values in each row.
    """

    def __init__(self, threshold: Union[float, int]=0.5):
        """
        Args:
            threshold (Union[float, int], optional): The threshold for the number of missing values in each row. If an integer, the row will be deleted if it has more than `threshold` missing values. If a float, the row will be deleted if it has more than `threshold` proportion of missing values. Defaults to 0.5.
        """
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be an integer or a float.")
        
        if isinstance(threshold, float) and not (0 <= threshold <= 1):
            raise ValueError("If threshold is a float, it must be between 0.0 and 1.0.")
        
        if isinstance(threshold, int) and threshold < 0:
            raise ValueError("If threshold is an integer, it must be non-negative.")
        
        self.threshold = threshold
        self.condition = None

    def fit(self, df: pd.DataFrame) -> 'ListWiseDeleterPandas':
        if isinstance(self.threshold, int):
            self.condition = df.isnull().sum(axis=1) < self.threshold
        elif isinstance(self.threshold, float) and 0 <= self.threshold <= 1:
            self.condition = (df.isnull().sum(axis=1) / len(df.columns)) < self.threshold
        
        return self
    
    def transform(self, df):
        if self.condition is None:
            raise ValueError("No condition to filter rows. Please fit the handler first.")
        
        df = df[self.condition]
        return df
    