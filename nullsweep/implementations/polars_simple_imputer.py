import polars as pl
from typing import Optional, Union


class PolarsImputer:
    def __init__(self, strategy: str = "mean", fill_value: Optional[Union[int, float, str]] = None):
        """
        Initialize the imputer.

        Args:
            strategy: The imputation strategy. Supported strategies are:
                      'mean', 'median', 'most_frequent', 'constant'.
            fill_value: The value to use for imputation when strategy is 'constant'.
        """
        if strategy not in ["mean", "median", "most_frequent", "constant"]:
            raise ValueError("Invalid strategy. Choose from 'mean', 'median', 'most_frequent', 'constant'.")
        self.strategy = strategy
        self.fill_value = fill_value
        self.imputation_value = None  # Stores the computed value for the column during fit

    def fit(self, column: pl.Series):
        """
        Compute the imputation value for the column based on the strategy.

        Args:
            column: The Polars Series (column) to fit the imputer on.
        """
        if self.strategy == "mean":
            self.imputation_value = column.mean()
        elif self.strategy == "median":
            self.imputation_value = column.median()
        elif self.strategy == "most_frequent":
            self.imputation_value = column.mode().first()
        elif self.strategy == "constant":
            if self.fill_value is None:
                raise ValueError("fill_value must be provided for strategy 'constant'.")
            self.imputation_value = self.fill_value
        else:
            raise ValueError(f"Unsupported strategy: {self.strategy}")

        return self

    def transform(self, column: pl.Series) -> pl.Series:
        """
        Impute missing values in the column using the computed imputation value.

        Args:
            column: The Polars Series (column) to transform.

        Returns:
            The transformed Polars Series with missing values imputed.
        """
        if self.imputation_value is None:
            raise RuntimeError("The imputer has not been fitted yet. Call 'fit' first.")

        return column.fill_null(self.imputation_value)

    def fit_transform(self, column: pl.Series) -> pl.Series:
        """
        Fit the imputer on the column and transform it in one step.

        Args:
            column: The Polars Series (column) to fit and transform.

        Returns:
            The transformed Polars Series with missing values imputed.
        """
        return self.fit(column).transform(column)