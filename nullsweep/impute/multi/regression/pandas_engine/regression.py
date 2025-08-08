import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LinearRegression
from typing import Optional, Union, Iterable, Any
from .....bases.handler import AHandler
from .....utils.decorators import to_pandas


class RegressionImputer(AHandler):
    """
    Impute missing values using regression models for specified columns.
    """

    def __init__(
            self, 
            column: Optional[Union[str, Iterable[str]]] = None, 
            estimator: Optional[Any]=None,
            predictor_strategy: str="mean"
            ):
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

    @to_pandas
    def fit(self, df):
        if self.column is None:
            self.column = df.columns[df.isnull().any()].tolist()
        elif isinstance(self.column, str):
            self.column = [self.column] 

        for col in self.column:
            missing_mask = df[col].isnull()
            non_missing_data = df.loc[~missing_mask]
            all_predictors = df.columns.drop(col)
            
            # Filter to only numeric predictors for regression
            numeric_predictors = [p for p in all_predictors if pd.api.types.is_numeric_dtype(df[p])]
            
            if len(numeric_predictors) == 0:
                raise ValueError(f"No numeric predictors available for column '{col}'. "
                               "Regression imputation requires at least one numeric predictor column.")

            X_train = self._fill_missing_predictors(non_missing_data[numeric_predictors])
            y_train = non_missing_data[col]

            estimator_clone = clone(self.estimator)
            estimator_clone.fit(X_train, y_train)

            self.estimators[col] = (estimator_clone, numeric_predictors)

        return self
    
    def _fill_missing_predictors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values in predictors based on the selected strategy."""
        result_df = df.copy()
        
        for col in df.columns:
            if df[col].isnull().any():
                col_dtype = df[col].dtype
                
                if self.predictor_strategy == "mean":
                    if pd.api.types.is_numeric_dtype(col_dtype):
                        fill_value = df[col].mean()
                    else:
                        fill_value = df[col].mode().iloc[0] if not df[col].mode().empty else df[col].dropna().iloc[0]
                elif self.predictor_strategy == "median":
                    if pd.api.types.is_numeric_dtype(col_dtype):
                        fill_value = df[col].median()
                    else:
                        fill_value = df[col].mode().iloc[0] if not df[col].mode().empty else df[col].dropna().iloc[0]
                elif self.predictor_strategy == "most_frequent":
                    fill_value = df[col].mode().iloc[0] if not df[col].mode().empty else df[col].dropna().iloc[0]
                else:
                    raise ValueError(f"Unknown predictor strategy: {self.predictor_strategy}")
                
                result_df[col] = result_df[col].fillna(fill_value)
        
        return result_df
    
    @to_pandas
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.estimators:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")
        
        for col, (estimator, numeric_predictors) in self.estimators.items():
            missing_mask = df[col].isnull()

            if missing_mask.any():
                missing_data = df.loc[missing_mask]

                X_missing = self._fill_missing_predictors(missing_data[numeric_predictors])

                predicted_values = estimator.predict(X_missing)

                df.loc[missing_mask, col] = predicted_values

        return df
    