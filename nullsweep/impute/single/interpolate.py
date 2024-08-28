import pandas as pd
import numpy as np


class LinearInterpolationImputer:

    """
    A class that applies linear interpolation to impute missing values in a pandas Series.
    Mimics the behavior of scikit-learn transformers with fit, fit_transform, and transform methods.
    """

    def __init__(self, method="linear", *args, **kwargs) -> None:
        self.method = method
        self.is_fitted = False

    def fit(self, X: pd.Series) -> None:
        """
        Fit the imputer. For linear interpolation, there's no fitting required.
        
        Args:
            X (pd.Series): The pandas Series to be imputed.

        Returns:
            self: Fitted instance of the transformer.
        """
        # Linear interpolation doesn't need any fitting, but we'll set a flag for compatibility
        if len(X) == 0:
            raise ValueError("Cannot fit an imputer on an empty Series")
        
        self.is_fitted = True
        return self
    
    def transform(self, X: pd.Series) -> pd.DataFrame:
        """
        Transform the data by applying linear interpolation to impute missing values.
        
        Args:
            X (pd.Series): The pandas Series to be transformed (with missing values imputed).
        
        Returns:
            pd.Series: The pandas Series with missing values imputed by linear interpolation.
        """
        if not self.is_fitted:
            raise RuntimeError("This LinearInterpolationImputer instance is not fitted yet. "
                               "Call 'fit' before calling 'transform'.")
        
        if isinstance(X, np.ndarray):
            X = pd.Series(X.flatten())
        
        return X.interpolate(method=self.method, limit_direction='both')
    
    def fit_transform(self, X: pd.Series) -> pd.Series:
        """
        Fit to data, then transform it.
        
        Args:
            X (pd.Series): The pandas Series to be transformed (with missing values imputed).
        
        Returns:
            pd.Series: The pandas Series with missing values imputed by linear interpolation.
        """
        return self.fit(X).transform(X)
    


   