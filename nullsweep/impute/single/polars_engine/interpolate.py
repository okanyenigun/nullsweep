import polars as pl
from ....bases.handler import AHandler


class LinearInterpolationImputerPolars(AHandler):
    def __init__(self, column: str, method: str = "linear", **kwargs):
        if method != "linear":
            raise ValueError(f"Polars only supports linear interpolation. Received: {method}")
        self.column = column
        self.method = method
        self.is_fitted = False

    def fit(self, df: pl.DataFrame) -> "LinearInterpolationImputerPolars":
        self.is_fitted = True
        return self
    
    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("Call 'fit' before 'transform'")
        
        return df.with_columns(
            pl.col(self.column)
            .interpolate()  
            .forward_fill()  
            .backward_fill() 
            .alias(self.column)
        )