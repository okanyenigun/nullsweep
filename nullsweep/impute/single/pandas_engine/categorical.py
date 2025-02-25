import pandas as pd
import numpy as np
from typing import Any
from ....bases.handler import AHandler


class SingleCategoricalImputer(AHandler):
    """
    Impute missing values in a single categorical column using specified strategies.
    """

    def __init__(self, column: str, strategy="most_frequent", fill_value: Any = None):
        """
        Args:
            column (str): The name of the column to impute.
            strategy (str, optional): The imputation strategy to use. Defaults to "most_frequent". Choices are "most_frequent", "constant", or "least_frequent".
            fill_value (Any, optional): The value to use for imputation when strategy is "constant". Defaults to None.
        """
        if strategy not in {"most_frequent", "constant", "least_frequent"}:
            raise ValueError("Strategy must be one of 'most_frequent', 'constant', or 'least_frequent'")
        
        self.column = column
        self.fill_value = fill_value
        self.strategy = strategy
        self.impute_value = None

    def fit(self, df: pd.DataFrame) -> 'SingleCategoricalImputer':
        self.impute_value = self._get_fit_value(df[self.column])
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.impute_value is None:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")
        df[self.column] = df[self.column].fillna(self.impute_value)
        return df

    def _get_fit_value(self, X: pd.Series) -> Any:
        """
        Determine the value to use for imputing missing values based on the chosen strategy.

        Args:
            X (pd.Series): The pandas Series to analyze.

        Returns:
            Any: The value to be used for imputation.
        """
        # Ensure X is a pandas Series
        if isinstance(X, np.ndarray):
            X = pd.Series(X.flatten())  # Flatten the array to ensure it's 1-dimensional

        if not isinstance(X, pd.Series):
            raise TypeError("`X` must be a pandas Series.")
        
        X_non_missing = X.dropna()
        
        if self.strategy == "most_frequent":
            if X_non_missing.empty:
                raise ValueError("No non-missing values to compute the most frequent value.")
            value = X_non_missing.mode().iloc[0]
        elif self.strategy == "constant":
            if self.fill_value is None:
                raise ValueError("`fill_value` must be specified for the 'constant' strategy.")
            value = self.fill_value
        elif self.strategy == "least_frequent":
            if X_non_missing.empty:
                raise ValueError("No non-missing values to compute the least frequent value.")
            category_counts = X_non_missing.value_counts()
            value = category_counts.idxmin()
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        return value