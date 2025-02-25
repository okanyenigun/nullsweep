import polars as pl
from typing import Any
from ....bases.handler import AHandler


class SingleCategoricalImputerPolars(AHandler):
    """
    Impute missing values in a single categorical column using specified strategies.
    """

    def __init__(self, column: str, strategy: str = "most_frequent", fill_value: Any = None):
        """
        Args:
            column (str): The name of the column to impute.
            strategy (str, optional): The imputation strategy to use. Defaults to "most_frequent".
                                     Choices are "most_frequent", "constant", or "least_frequent".
            fill_value (Any, optional): The value to use for imputation when strategy is "constant".
                                       Defaults to None.
        """
        if strategy not in {"most_frequent", "constant", "least_frequent"}:
            raise ValueError("Strategy must be one of 'most_frequent', 'constant', or 'least_frequent'")
        
        self.column = column
        self.strategy = strategy
        self.fill_value = fill_value
        self.impute_value = None

    def fit(self, df: pl.DataFrame) -> 'SingleCategoricalImputerPolars':
        """
        Compute the imputation value for the specified column based on the chosen strategy.

        Args:
            df (pl.DataFrame): The Polars DataFrame containing the column to fit.

        Returns:
            SingleCategoricalImputer: The fitted imputer.
        """
        self.impute_value = self._get_fit_value(df[self.column])
        return self

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Impute missing values in the specified column using the computed imputation value.

        Args:
            df (pl.DataFrame): The Polars DataFrame to transform.

        Returns:
            pl.DataFrame: The transformed DataFrame with missing values imputed.
        """
        if self.impute_value is None:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")
        
        # Update the column with the imputed value
        df = df.with_columns(pl.col(self.column).fill_null(self.impute_value))
        return df

    def _get_fit_value(self, X: pl.Series) -> Any:
        """
        Determine the value to use for imputing missing values based on the chosen strategy.

        Args:
            X (pl.Series): The Polars Series to analyze.

        Returns:
            Any: The value to be used for imputation.
        """
        if not isinstance(X, pl.Series):
            raise TypeError("`X` must be a Polars Series.")
        
        # Drop null values
        X_non_missing = X.drop_nulls()
        
        if self.strategy == "most_frequent":
            if X_non_missing.is_empty():
                raise ValueError("No non-missing values to compute the most frequent value.")
            value = X_non_missing.mode().first()  # Get the first mode
        elif self.strategy == "constant":
            if self.fill_value is None:
                raise ValueError("`fill_value` must be specified for the 'constant' strategy.")
            value = self.fill_value
        elif self.strategy == "least_frequent":
            if X_non_missing.is_empty():
                raise ValueError("No non-missing values to compute the least frequent value.")
            category_counts = X_non_missing.value_counts()
            value = category_counts.filter(pl.col("counts") == category_counts["counts"].min())["value"].first()
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        return value