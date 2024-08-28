import pandas as pd
import numpy as np


class DirectionFillImputer:
    """
    A class that wraps forward fill and backward fill for imputing missing values in a pandas Series.
    Mimics the behavior of scikit-learn transformers with fit, fit_transform, and transform methods.
    The strategy can be set to 'forward' or 'backward' to determine the fill direction.
    """
    
    def __init__(self, strategy='forwardfill'):
        """
        Initialize the imputer with the chosen strategy.
        
        Args:
            strategy (str): The fill strategy to use, either 'forwardfill' or 'backfill'.
                            Default is 'forwardfill'.
        
        Raises:
            ValueError: If the strategy is not one of 'forwardfill' or 'backfill'.
        """
        if strategy not in ['forwardfill', 'backfill']:
            raise ValueError("Strategy must be either 'forwardfill' or 'backfill'.")
        self.strategy = strategy
        self.is_fitted = False
    
    def fit(self, X: pd.Series):
        """
        Fit the imputer. For forward/backward fill, there's no fitting required.
        
        Args:
            X (pd.Series): The pandas Series to be imputed.
        
        Returns:
            self: Fitted instance of the transformer.
        """
        self.is_fitted = True
        return self
    
    def transform(self, X: pd.Series) -> pd.Series:
        """
        Transform the data by applying the chosen fill strategy to impute missing values.
        
        Args:
            X (pd.Series): The pandas Series to be transformed (with missing values imputed).
        
        Returns:
            pd.Series: The pandas Series with missing values imputed by the chosen strategy.
        """
        if not self.is_fitted:
            raise RuntimeError("This FillImputer instance is not fitted yet. "
                               "Call 'fit' before calling 'transform'.")
        
        # Ensure X is a pandas Series
        if isinstance(X, np.ndarray):
            X = pd.Series(X.flatten())  # Flatten the array to ensure it's 1-dimensional
        
        if self.strategy == 'forwardfill':
            return X.ffill()
        elif self.strategy == 'backfill':
            return X.bfill()
    
    def fit_transform(self, X: pd.Series) -> pd.Series:
        """
        Fit to data, then transform it using the chosen fill strategy.
        
        Args:
            X (pd.Series): The pandas Series to be transformed (with missing values imputed).
        
        Returns:
            pd.Series: The pandas Series with missing values imputed by the chosen strategy.
        """
        return self.fit(X).transform(X)
