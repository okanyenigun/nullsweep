import pandas as pd
from ...bases.handler import AHandler


class DirectionFillImputer(AHandler):
    """
    A class that wraps forward fill and backward fill for imputing missing values in a pandas Series.
    Mimics the behavior of scikit-learn transformers with fit, fit_transform, and transform methods.
    The strategy can be set to 'forward' or 'backward' to determine the fill direction.
    """
    
    def __init__(self, column: str, strategy='forwardfill'):
        if strategy not in ['forwardfill', 'backfill']:
            raise ValueError("Strategy must be either 'forwardfill' or 'backfill'.")
        if not isinstance(column, str):
            raise TypeError("`column` must be a string representing the column name.")
        
        self.column = column
        self.strategy = strategy
        self.is_fitted = False
    
    def fit(self, df: pd.DataFrame) -> 'DirectionFillImputer':
        self.is_fitted = True
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("This FillImputer instance is not fitted yet. "
                               "Call 'fit' before calling 'transform'.")
         
        if self.strategy == 'forwardfill':
            df[self.column] = df[self.column].ffill() 
        elif self.strategy == 'backfill':
            df[self.column] = df[self.column].bfill()

        return df