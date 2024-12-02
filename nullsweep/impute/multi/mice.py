import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from typing import Optional, Union, Iterable, Any
from ...bases.handler import AHandler


class MICEImputer(AHandler):
    """
    A wrapper for sklearn's IterativeImputer to handle multivariate imputation
    for missing values in DataFrames.
    """

    def __init__(self, 
                 column: Optional[Union[Iterable, str]] = None, 
                 estimator: Optional[Any]=None, 
                 max_iter: int=10, 
                 random_state: Optional[Any]=None):
        """
        Args:
            column (Optional[Union[Iterable, str]], optional): . Defaults to None.
            estimator (Optional[Any], optional): Estimator to use for imputation. Defaults to None.
            max_iter (int, optional): Maximum number of imputation rounds. Defaults to 10.
            random_state (Optional[Any], optional): Random state for reproducibility. Defaults to None.
        """
        if not isinstance(max_iter, int) or max_iter <= 0:
            raise ValueError("`max_iter` must be a positive integer.")
        self.column = column
        self.estimator = estimator
        self.max_iter = max_iter
        self.random_state = random_state
        self.imputer = None
        self.target_columns = None

    def fit(self, df: pd.DataFrame) -> 'MICEImputer':
        if self.column is None:
            self.target_columns = df.columns[df.isnull().any()].tolist()
        elif isinstance(self.column, str):
            self.target_columns = [self.column]
        else:
            self.target_columns = list(self.column)

        # Validate target columns
        missing_columns = [col for col in self.target_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Target column(s) {missing_columns} not found in the DataFrame.")

        # Ensure there are missing values in the target columns
        if not any(df[self.target_columns].isnull().any()):
            raise ValueError("No missing values found in the specified target columns.")

        # Fit the imputer on the entire DataFrame
        self.imputer = IterativeImputer(
            estimator=self.estimator,
            max_iter=self.max_iter,
            random_state=self.random_state,
        )
        self.imputer.fit(df)

        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.imputer is None:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")

        # Copy the DataFrame to ensure immutability
        df_copy = df.copy()

        # Apply MICE imputation
        imputed_array = self.imputer.transform(df_copy)
        imputed_df = pd.DataFrame(imputed_array, columns=df.columns, index=df.index)

        # Update only the target columns
        df_copy[self.target_columns] = imputed_df[self.target_columns]

        return df_copy
