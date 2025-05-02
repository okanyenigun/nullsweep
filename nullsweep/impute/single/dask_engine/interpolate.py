import dask.dataframe as dd
from ....bases.handler import AHandler


class LinearInterpolationImputerDask(AHandler):

    def __init__(self, column: str, method: str = "linear", **kwargs):
        if method != "linear":
            raise ValueError(
                f"Dask-based interpolation currently only supports 'linear'. Received: {method}."
            )
        if not isinstance(column, str):
            raise TypeError("`column` must be a string representing the column name.")
        self.column = column
        self.method = method
        self.is_fitted = False

    def fit(self, df: dd.DataFrame) -> "LinearInterpolationImputerDask":
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in DataFrame.")
        
        self.is_fitted = True
        return self

    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError(
                "This LinearInterpolationImputerDask instance is not fitted yet. "
                "Call 'fit' before 'transform'."
            )

        def _interpolate_partition(pdf):
            pdf[self.column] = pdf[self.column].interpolate(
                method=self.method,
                limit_direction="both"
            )
            return pdf

        return df.map_partitions(_interpolate_partition)

    def fit_transform(self, df: dd.DataFrame) -> dd.DataFrame:
        return self.fit(df).transform(df)
