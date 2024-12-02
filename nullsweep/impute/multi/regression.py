import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LinearRegression
from typing import Optional, Union, Iterable, Any
from ...bases.handler import AHandler


class RegressionImputer(AHandler):
    """
    Impute missing values using regression models for specified columns.
    """

    def __init__(self, 
                 column: Optional[Union[str, Iterable[str]]] = None, 
                 estimator: Optional[Any]=None,
                 predictor_strategy: str="mean"):
        """
        Args:
            column (Optional[Union[str, Iterable[str]]], optional): Defaults to None.
            estimator (Optional[Any], optional): Estimator to use for imputation. Defaults to None.
            predictor_strategy (str, optional): Strategy to use for imputing missing predictors. Defaults to "mean". Can be one of "mean", "median", or "most_frequent".
        """
        if predictor_strategy not in {"mean", "median", "most_frequent"}:
            raise ValueError("`predictor_strategy` must be one of 'mean', 'median', or 'most_frequent'.")
        
        self.column = column
        self.estimator = estimator if estimator is not None else LinearRegression()
        self.estimators = {}
        self.predictor_strategy = predictor_strategy

    def fit(self, df):
        if self.column is None:
            self.column = df.columns[df.isnull().any()].tolist()
        elif isinstance(self.column, str):
            self.column = [self.column] 

        for col in self.column:
            missing_mask = df[col].isnull()
            non_missing_data = df.loc[~missing_mask]
            predictors = df.columns.drop(col)

            X_train = self._fill_missing_predictors(non_missing_data[predictors])

            y_train = non_missing_data[col]

            estimator_clone = clone(self.estimator)
            estimator_clone.fit(X_train, y_train)

            self.estimators[col] = estimator_clone

        return self
    
    def _fill_missing_predictors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values in predictors based on the selected strategy."""
        if self.predictor_strategy == "mean":
            return df.fillna(df.mean())
        elif self.predictor_strategy == "median":
            return df.fillna(df.median())
        elif self.predictor_strategy == "most_frequent":
            return df.fillna(df.mode().iloc[0])
        else:
            raise ValueError(f"Unknown predictor strategy: {self.predictor_strategy}")
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.estimators:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")
        
        for col, estimator in self.estimators.items():
            missing_mask = df[col].isnull()

            if missing_mask.any():
                missing_data = df.loc[missing_mask]

                predictors = df.columns.drop(col)
                X_missing = self._fill_missing_predictors(missing_data[predictors])

                predicted_values = estimator.predict(X_missing)

                df.loc[missing_mask, col] = predicted_values

        return df
    