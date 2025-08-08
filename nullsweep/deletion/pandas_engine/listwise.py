import pandas as pd
from typing import Union, Optional, List
from ...bases.handler import AHandler


class ListWiseDeleterPandas(AHandler):
    """
    A class to delete rows from a DataFrame based on the number of missing values in each row.
    """

    def __init__(self, threshold: Union[float, int]=0.5, column: Optional[Union[str, List[str]]]=None):
        """
        Args:
            threshold (Union[float, int], optional): The threshold for the number of missing values in each row. 
                If an integer, the row will be deleted if it has more than `threshold` missing values. 
                If a float, the row will be deleted if it has more than `threshold` proportion of missing values. 
                Defaults to 0.5.
            column (Optional[Union[str, List[str]]], optional): Specific column(s) to consider for missing values.
                If None, considers all columns. Defaults to None.
        """
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be an integer or a float.")
        
        if isinstance(threshold, float) and not (0 <= threshold <= 1):
            raise ValueError("If threshold is a float, it must be between 0.0 and 1.0.")
        
        if isinstance(threshold, int) and threshold < 0:
            raise ValueError("If threshold is an integer, it must be non-negative.")
        
        self.threshold = threshold
        self.column = column
        self.condition = None
        self.columns_to_check = None

    def fit(self, df: pd.DataFrame) -> 'ListWiseDeleterPandas':
        # Determine which columns to check for missing values
        if self.column is None:
            self.columns_to_check = df.columns.tolist()
        else:
            if isinstance(self.column, str):
                self.columns_to_check = [self.column]
            else:
                self.columns_to_check = list(self.column)
            
            # Validate that columns exist in DataFrame
            missing_cols = [col for col in self.columns_to_check if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Columns {missing_cols} not found in DataFrame")

        # Calculate missing values only for specified columns
        df_subset = df[self.columns_to_check]
        
        if isinstance(self.threshold, int):
            self.condition = df_subset.isnull().sum(axis=1) < self.threshold
        elif isinstance(self.threshold, float) and 0 <= self.threshold <= 1:
            self.condition = (df_subset.isnull().sum(axis=1) / len(self.columns_to_check)) < self.threshold
        
        return self
    
    def transform(self, df):
        if self.condition is None:
            raise ValueError("No condition to filter rows. Please fit the handler first.")
        
        df = df[self.condition]
        return df
    