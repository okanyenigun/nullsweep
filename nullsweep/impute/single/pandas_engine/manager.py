import pandas as pd
from typing import Union, Any, Dict, Optional, Iterable
from .categorical import SingleCategoricalImputer
from .continuous import SimpleImputerWrapper
from .interpolate import LinearInterpolationImputerPandas
from .direction import DirectionFillImputer
from .decision import SingleImputationStrategyDecider
from ....utils.structs import Structs


class SingleImputationPandas:
    """
    A wrapper for single imputations using dynamic strategy selection.
    """
    def __init__(self, 
                 impute_strategy: str, 
                 column: Optional[Union[Iterable, str]] = None,
                 strategy_decider: Any=SingleImputationStrategyDecider,
                 fill_value: Optional[Any]=None,
                 strategy_params: Optional[Dict[str, Any]]=None
                 ):
        """
        Args:
            impute_strategy (str): The imputation strategy to use. Must be one of: "auto", "mean", "median", "most_frequent", "constant", "interpolate", "backfill", "forwardfill".
            column (Optional[Union[Iterable, str]], optional): The column(s) to impute. If None, all columns with missing values will be imputed. Defaults to None.
            strategy_decider (Any, optional): Decides the imputation strategy if "auto" is selected. Defaults to SingleImputationStrategyDecider.
            fill_value (Optional[Any], optional): The fill value to use for constant imputation. Defaults to None.
            strategy_params (Optional[Dict[str, Any]], optional): Additional parameters to pass to the imputer. Defaults to None.
        """
        if not isinstance(impute_strategy, str):
            raise TypeError("`impute_strategy` must be a string.")
        
        self.column = column
        self.impute_strategy = impute_strategy
        self.fill_value = fill_value
        self.strategy_params = strategy_params or {}
        self.imputers = {} 
        self._decider = strategy_decider()
        self._imputers = {
            "continuous": {
                "mean": SimpleImputerWrapper,
                "median": SimpleImputerWrapper,
                "most_frequent": SimpleImputerWrapper,
                "constant": SimpleImputerWrapper,
                "interpolate": LinearInterpolationImputerPandas,
                "backfill": DirectionFillImputer,
                "forwardfill": DirectionFillImputer,
            },
            "categorical": {
                "most_frequent": SingleCategoricalImputer,
                "constant": SingleCategoricalImputer,
                "least_frequent": SingleCategoricalImputer,
                "backfill": DirectionFillImputer,
                "forwardfill": DirectionFillImputer,
            },
            "date":{
                "interpolate": LinearInterpolationImputerPandas,
                "backfill": DirectionFillImputer,
                "forwardfill": DirectionFillImputer,
            }
        }

    def fit(self, df: pd.DataFrame) -> "SingleImputationPandas":
        self.column = self._determine_columns(df)
        for col in self.column:
            # Determine strategy if "auto"
            strategy = self.impute_strategy
            if strategy == "auto" or strategy is None:
                strategy = self._decider.decide_imputation_strategy(df[col])

            # Prepare strategy-specific parameters
            self._fix_strategy_params(col, strategy)

            # Set and fit the imputer for the column
            self._set_imputer(df, col)
            self.imputers[col].fit(df)

        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.imputers:
            raise RuntimeError("This SingleImputationWrapper instance is not fitted yet. "
                               "Call 'fit' before calling 'transform'.")

        for col in self.column:
            df = self.imputers[col].transform(df)

        return df
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df)

    def _determine_columns(self, df: pd.DataFrame) -> list:
        """
        Determine columns to impute based on the provided column parameter.
        """
        if self.column is None:
            # If column is None, select all columns with missing values
            return df.columns[df.isnull().any()].tolist()
        elif isinstance(self.column, str):
            # Single column provided as a string
            return [self.column]
        elif isinstance(self.column, Iterable):
            # List of columns
            missing_columns = [col for col in self.column if col in df.columns and df[col].isnull().any()]
            if not missing_columns:
                raise ValueError("None of the specified columns have missing values.")
            return missing_columns
        else:
            raise ValueError("Invalid column type. Must be None, a string, or an iterable of column names.")
    
    def _fix_strategy_params(self, column: str, strategy: str):
        """
        Prepare strategy-specific parameters for the given column and strategy.
        """
        # Ensure strategy and column are set
        self.strategy_params["strategy"] = strategy
        self.strategy_params["column"] = column

        # Add fill_value if specified
        if self.fill_value is not None:
            self.strategy_params["fill_value"] = self.fill_value

        return
    
    def _set_imputer(self, df: pd.DataFrame, column: str):
        """
        Set the appropriate imputer for the given column.
        """
        series = df[column]
        feature_type = Structs.detect_series_type(series)
        strategy = self.strategy_params.get("strategy")

        imputer = self._imputers.get(feature_type, {}).get(strategy)
        if imputer is None:
            raise ValueError(f"Invalid imputation strategy '{strategy}'. For {feature_type} type of features, "
                             f"the strategy must be one of: {list(self._imputers[feature_type].keys())}")

        # Initialize the imputer for this column
        self.imputers[column] = imputer(**self.strategy_params)
        return
