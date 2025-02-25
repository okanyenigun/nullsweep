import polars as pl
from ....bases.handler import AHandler


class DirectionFillImputerPolars(AHandler):
    """
    A class that wraps forward fill and backward fill for imputing missing values in a Polars Series.
    Mimics the behavior of scikit-learn transformers with fit, fit_transform, and transform methods.
    The strategy can be set to 'forwardfill' or 'backfill' to determine the fill direction.
    """
    
    def __init__(self, column: str, strategy: str = 'forwardfill'):
        """
        Args:
            column (str): The name of the column to impute.
            strategy (str, optional): The imputation strategy to use. Defaults to 'forwardfill'.
                                     Choices are 'forwardfill' or 'backfill'.
        """
        if strategy not in ['forwardfill', 'backfill']:
            raise ValueError("Strategy must be either 'forwardfill' or 'backfill'.")
        if not isinstance(column, str):
            raise TypeError("`column` must be a string representing the column name.")
        
        self.column = column
        self.strategy = strategy
        self.is_fitted = False
    
    def fit(self, df: pl.DataFrame) -> 'DirectionFillImputerPolars':
        """
        Fit the imputer. This method does not compute anything but is required for consistency
        with the scikit-learn transformer interface.

        Args:
            df (pl.DataFrame): The Polars DataFrame containing the column to fit.

        Returns:
            DirectionFillImputer: The fitted imputer.
        """
        self.is_fitted = True
        return self
    
    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Impute missing values in the specified column using the chosen fill strategy.

        Args:
            df (pl.DataFrame): The Polars DataFrame to transform.

        Returns:
            pl.DataFrame: The transformed DataFrame with missing values imputed.
        """
        if not self.is_fitted:
            raise RuntimeError("This FillImputer instance is not fitted yet. "
                               "Call 'fit' before calling 'transform'.")
        
        if self.strategy == 'forwardfill':
            df = df.with_columns(pl.col(self.column).forward_fill())
        elif self.strategy == 'backfill':
            df = df.with_columns(pl.col(self.column).backward_fill())
        
        return df

    def fit_transform(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Fit the imputer and transform the DataFrame in one step.

        Args:
            df (pl.DataFrame): The Polars DataFrame to fit and transform.

        Returns:
            pl.DataFrame: The transformed DataFrame with missing values imputed.
        """
        return self.fit(df).transform(df)