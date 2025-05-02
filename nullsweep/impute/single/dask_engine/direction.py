import dask.dataframe as dd
from ....bases.handler import AHandler


class DirectionFillImputerDask(AHandler):
    
    def __init__(self, column: str, strategy: str = 'forwardfill'):
        if strategy not in ['forwardfill', 'backfill']:
            raise ValueError("Strategy must be either 'forwardfill' or 'backfill'.")
        if not isinstance(column, str):
            raise TypeError("`column` must be a string representing the column name.")
        self.column = column
        self.strategy = strategy
        self.is_fitted = False

    def fit(self, df: dd.DataFrame) -> 'DirectionFillImputerDask':
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in DataFrame.")
        self.is_fitted = True
        return self

    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("This DirectionFillImputerDask instance is not fitted yet. Call 'fit' before 'transform'.")
        if self.strategy == 'forwardfill':
            filled = df[self.column].ffill()
        else:
            filled = df[self.column].bfill()
        return df.assign(**{self.column: filled})

    def fit_transform(self, df: dd.DataFrame) -> dd.DataFrame:
        return self.fit(df).transform(df)
