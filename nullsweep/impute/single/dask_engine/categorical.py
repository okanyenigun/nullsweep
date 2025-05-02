import dask.dataframe as dd
from typing import Any
from ....bases.handler import AHandler


class SingleCategoricalImputerDask(AHandler):

    def __init__(self, column: str, strategy: str = "most_frequent", fill_value: Any = None):
        if strategy not in {"most_frequent", "constant", "least_frequent"}:
            raise ValueError("Strategy must be one of 'most_frequent', 'constant', or 'least_frequent'")
        self.column = column
        self.strategy = strategy
        self.fill_value = fill_value
        self.impute_value: Any = None

    def fit(self, df: dd.DataFrame) -> 'SingleCategoricalImputerDask':
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in DataFrame.")

        if self.strategy == "constant":
            if self.fill_value is None:
                raise ValueError("`fill_value` must be specified for the 'constant' strategy.")
            self.impute_value = self.fill_value

        else:
            vc = df[self.column].value_counts().compute()
            if vc.empty:
                raise ValueError("No non-missing values to compute imputation value.")

            if self.strategy == "most_frequent":
                self.impute_value = vc.index[0]
            else:  # least_frequent
                self.impute_value = vc.index[-1]

        return self

    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if self.impute_value is None:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")

        filled = df[self.column].fillna(self.impute_value)
        return df.assign(**{self.column: filled})

    def fit_transform(self, df: dd.DataFrame) -> dd.DataFrame:
        return self.fit(df).transform(df)
