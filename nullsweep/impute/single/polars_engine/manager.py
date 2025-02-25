import polars as pl
from typing import Any, Dict, Iterable, Optional, Union
from .categorical import SingleCategoricalImputerPolars
from .continuous import SimpleImputerWrapperPolars
from .interpolate import LinearInterpolationImputerPolars
from .direction import DirectionFillImputerPolars
from ..pandas_engine.decision import SingleImputationStrategyDecider
from ....utils.structs import Structs

class SingleImputationPolars:

    def __init__(
        self, 
        impute_strategy: str, 
        column: Optional[Union[Iterable, str]] = None,
        strategy_decider: Any=SingleImputationStrategyDecider,
        fill_value: Optional[Any]=None,
        strategy_params: Optional[Dict[str, Any]]=None
        ):

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
                "mean": SimpleImputerWrapperPolars,
                "median": SimpleImputerWrapperPolars,
                "most_frequent": SimpleImputerWrapperPolars,
                "constant": SimpleImputerWrapperPolars,
                "interpolate": LinearInterpolationImputerPolars,
                "backfill": DirectionFillImputerPolars,
                "forwardfill": DirectionFillImputerPolars,
            },
            "categorical": {
                "most_frequent": SingleCategoricalImputerPolars,
                "constant": SingleCategoricalImputerPolars,
                "least_frequent": SingleCategoricalImputerPolars,
                "backfill": DirectionFillImputerPolars,
                "forwardfill": DirectionFillImputerPolars,
            },
            "date":{
                "interpolate": LinearInterpolationImputerPolars,
                "backfill": DirectionFillImputerPolars,
                "forwardfill": DirectionFillImputerPolars,
            }
        }

    def fit(self, df: pl.DataFrame) -> "SingleImputationPolars":
        self.column = self._determine_columns(df)
        for col in self.column:
            strategy = self.impute_strategy
            if strategy == "auto" or strategy is None:
                strategy = self._decider.decide_imputation_strategy(df[col])

            self._fix_strategy_params(col, strategy)

            # Set and fit the imputer for the column
            self._set_imputer(df, col)
            self.imputers[col].fit(df)

        return self
    
    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if not self.imputers:
            raise RuntimeError("This SingleImputationWrapper instance is not fitted yet. "
                               "Call 'fit' before calling 'transform'.")

        for col in self.column:
            df = self.imputers[col].transform(df)

        return df
    
    def fit_transform(self, df: pl.DataFrame) -> pl.DataFrame:
        self.fit(df)
        return self.transform(df)

    def _determine_columns(self, df: pl.DataFrame) -> list:
        """
        Determine columns to impute based on the provided column parameter.
        """
        if self.column is None:
            # If column is None, select all columns with missing values
            columns_with_nulls = df.select(pl.all().is_null().any()).row(0)
            return [col for col, has_null in zip(df.columns, columns_with_nulls) if has_null]
        elif isinstance(self.column, str):
            # Single column provided as a string
            if self.column not in df.columns:
                raise ValueError(f"Column '{self.column}' not found in the DataFrame.")
            return [self.column]
        elif isinstance(self.column, Iterable):
            # List of columns
            missing_columns = [col for col in self.column if col in df.columns and df.select(pl.col(col).is_null().any()).row(0)[0]]
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
    
    def _set_imputer(self, df: pl.DataFrame, column: str):
        """
        Set the appropriate imputer for the given column.
        """
        series = df[column]
        feature_type = Structs.detect_series_type_polars(series)
        strategy = self.strategy_params.get("strategy")

        imputer = self._imputers.get(feature_type, {}).get(strategy)
        if imputer is None:
            raise ValueError(f"Invalid imputation strategy '{strategy}'. For {feature_type} type of features, "
                             f"the strategy must be one of: {list(self._imputers[feature_type].keys())}")

        # Initialize the imputer for this column
        self.imputers[column] = imputer(**self.strategy_params)
        return
