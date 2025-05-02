import dask.dataframe as dd
from typing import Any
from ....bases.handler import AHandler


class SimpleImputerDask(AHandler):

    def __init__(self, column: str, strategy: str = "mean", fill_value: Any = None):
        if strategy not in {"mean", "median", "most_frequent", "constant"}:
            raise ValueError("Strategy must be one of 'mean', 'median', 'most_frequent', or 'constant'.")
        self.column = column
        self.strategy = strategy
        self.fill_value = fill_value
        self.impute_value: Any = None

    def fit(self, df: dd.DataFrame) -> 'SimpleImputerDask':
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in DataFrame.")

        if self.strategy == "constant":
            if self.fill_value is None:
                raise ValueError("'fill_value' must be provided for 'constant' strategy.")
            self.impute_value = self.fill_value
        else:
            if self.strategy == "mean":
                self.impute_value = df[self.column].mean().compute()
            elif self.strategy == "median":
                self.impute_value = df[self.column].quantile(0.5).compute()
            else:  # most_frequent
                vc = df[self.column].value_counts().compute()
                if vc.empty:
                    raise ValueError("No non-missing values to determine most_frequent.")
                self.impute_value = vc.index[0]

        return self

    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if self.impute_value is None:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")

        filled = df[self.column].fillna(self.impute_value)
        return df.assign(**{self.column: filled})

    def fit_transform(self, df: dd.DataFrame) -> dd.DataFrame:
        return self.fit(df).transform(df)
