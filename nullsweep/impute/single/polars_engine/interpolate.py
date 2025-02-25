import polars as pl
from ....bases.handler import AHandler


class LinearInterpolationImputerPolars(AHandler):

    def __init__(self, column: str, method: str="linear", **kwargs):
        if method != "linear":
            raise ValueError(f"Polars only supports linear interpolation. Received method: {method}. Please use 'linear' as the method argument.")

        self.column = column
        self.method = method
        self.is_fitted = False

    def fit(self, df: pl.DataFrame) -> "LinearInterpolationImputerPolars":
        self.is_fitted = True
        return self
    
    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("This LinearInterpolationImputer instance is not fitted yet. "
                               "Call 'fit' before calling 'transform'.")
        
        df = df.with_columns(
            pl.col(self.column).interpolate().alias(self.column)
        )
        return df
            