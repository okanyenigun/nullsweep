import pandas as pd
from ...bases.handler import AHandler


class LinearInterpolationImputer(AHandler):

    """
    A class that applies linear interpolation to impute missing values in a pandas Series.
    Mimics the behavior of scikit-learn transformers with fit, fit_transform, and transform methods.
    """

    def __init__(self, column: str, method: str="linear", **kwargs):
        self.column = column
        self.method = method
        self.is_fitted = False

    def fit(self, df: pd.DataFrame) -> "LinearInterpolationImputer":
        self.is_fitted = True
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("This LinearInterpolationImputer instance is not fitted yet. "
                               "Call 'fit' before calling 'transform'.")
        
        df[self.column] = df[self.column].interpolate(method=self.method, limit_direction='both')
        return df
    