import pandas as pd
from sklearn.impute import KNNImputer
from typing import Optional, Union, Iterable
from .....bases.handler import AHandler
from .....utils.decorators import to_pandas


class KNNImputerWrapper(AHandler):
    """
    A wrapper for sklearn's KNNImputer to handle missing values in DataFrames.
    """

    def __init__(self, column: Optional[Union[Iterable, str]] = None, n_neighbors: int = 5):
        if not isinstance(n_neighbors, int) or n_neighbors <= 0:
            raise ValueError("`n_neighbors` must be a positive integer.")
        self.column = column
        self.n_neighbors = n_neighbors
        self.imputer = None
        self.target_columns = None  # Columns to be imputed

    @to_pandas
    def fit(self, df: pd.DataFrame) -> 'KNNImputerWrapper':
        if self.column is None:
            self.target_columns = df.columns[df.isnull().any()].tolist()
        elif isinstance(self.column, str):
            self.target_columns = [self.column]
        else:
            self.target_columns = list(self.column)

        # Validate that target columns exist
        missing_columns = [col for col in self.target_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Target column(s) {missing_columns} not found in the DataFrame.")

        # Validate that there are missing values to impute
        if not any(df[self.target_columns].isnull().any()):
            raise ValueError("No missing values found in the specified target columns.")

        # Fit the imputer on the relevant DataFrame slice
        self.imputer = KNNImputer(n_neighbors=self.n_neighbors)
        self.imputer.fit(df[self.target_columns])

        return self

    @to_pandas
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.imputer is None:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")

        # Copy the DataFrame to ensure immutability
        df_copy = df.copy()

        # Impute missing values in the specified columns
        imputed_values = self.imputer.transform(df_copy[self.target_columns])
        imputed_df = pd.DataFrame(
            imputed_values, columns=self.target_columns, index=df_copy.index
        )

        # Assign imputed values back to the original DataFrame columns
        df_copy[self.target_columns] = imputed_df

        return df_copy
