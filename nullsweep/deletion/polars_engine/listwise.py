import polars as pl
from typing import Union
from ...bases.handler import AHandler

class ListWiseDeleterPolars(AHandler):
    """
    A class to delete rows from a Polars DataFrame based on the number or proportion of missing values in each row.
    """
    def __init__(self, threshold: Union[float, int] = 0.5):
        """
        Args:
            threshold (Union[float, int], optional): The threshold for missing values in each row.
                - If an integer, a row is kept only if it has fewer than `threshold` missing values.
                - If a float (between 0 and 1), a row is kept only if the proportion of missing values is less than `threshold`.
                Defaults to 0.5.
        """
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be an integer or a float.")
        if isinstance(threshold, float) and not (0 <= threshold <= 1):
            raise ValueError("If threshold is a float, it must be between 0.0 and 1.0.")
        if isinstance(threshold, int) and threshold < 0:
            raise ValueError("If threshold is an integer, it must be non-negative.")
        
        self.threshold = threshold
        self.condition = None

    def fit(self, df: pl.DataFrame) -> 'ListWiseDeleterPolars':
        # Create an expression list: for each column, 1 if not null, 0 if null.
        non_null_exprs = [pl.col(c).is_not_null().cast(pl.Int8) for c in df.columns]
        # Compute the row-wise sum of non-null values.
        condition_df = df.select(pl.sum_horizontal(non_null_exprs).alias("non_null_count"))
        
        # For an integer threshold, keep rows with missing_count < threshold,
        # which is equivalent to non_null_count > (df.width - threshold)
        if isinstance(self.threshold, int):
            self.condition = (condition_df["non_null_count"] > (df.width - self.threshold))
        # For a float threshold, keep rows with missing proportion less than threshold,
        # i.e. non_null_count/df.width > 1 - threshold.
        else:
            self.condition = ((condition_df["non_null_count"] / df.width) > (1 - self.threshold))
        
        return self

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if self.condition is None:
            raise ValueError("No condition to filter rows. Please fit the handler first.")
        # Filter the DataFrame using the Boolean mask stored in self.condition.
        return df.filter(self.condition)
