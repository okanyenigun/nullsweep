import pandas as pd
import numpy as np
from typing import Any


class SingleCategoricalImputer:

    def __init__(self, strategy="most_frequent", fill_value: Any = None) -> None:
        if strategy not in {"most_frequent", "constant", "least_frequent"}:
            raise ValueError("Strategy must be one of 'most_frequent', 'constant', or 'least_frequent'")

        self.fill_value = fill_value
        self.strategy = strategy

    def fit(self, X: pd.Series) -> None:
        """
        Fit the imputer on the provided pandas Series.

        Args:
            X (pd.Series): The pandas Series to be imputed.

        Returns:
            None
        """
        if len(X) == 0:
            raise ValueError("Cannot fit on an empty Series")
        
        self.fill_value = self._get_fit_value(X)
        return
    
    def fit_transform(self, X: pd.Series) -> pd.Series:
        """
        Fit the imputer on the provided pandas Series, then transform the series.

        Args:
            X (pd.Series): The pandas Series to be imputed.

        Returns:
            pd.Series: The transformed pandas Series with imputed values.
        """
        self.fit(X)
        return self.transform(X)
    
    def transform(self, X: pd.Series) -> pd.Series:
        """
        Transform the provided pandas Series by imputing missing values.

        Args:
            X (pd.Series): The pandas Series to be imputed.

        Returns:
            pd.Series: The transformed pandas Series with imputed values.
        """
        # Ensure X is a pandas Series
        if isinstance(X, np.ndarray):
            X = pd.Series(X.flatten())  # Flatten the array to ensure it's 1-dimensional

        if self.fill_value is None:
            raise ValueError("The imputer has not been fitted. Please call 'fit' before 'transform'.")

        return X.fillna(self.fill_value)

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
        
        if self.strategy == "most_frequent":
            value = X.mode()[0]
        elif self.strategy == "constant":
            value = self.fill_value
        elif self.strategy == "least_frequent":
            category_counts = X.value_counts()
            value = category_counts.idxmin()
        return value
