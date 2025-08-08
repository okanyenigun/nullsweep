from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.functions import col, isnan
from typing import Optional, Union, Iterable, Any, Dict
from .categorical import SingleCategoricalImputerSpark
from .continuous import SimpleImputerSpark
from .interpolate import LinearInterpolationImputerSpark
from .direction import DirectionFillImputerSpark
from ..pandas_engine.decision import SingleImputationStrategyDecider
from ....bases.handler import AHandler
from ....utils.structs import Structs


class SingleImputationSpark(AHandler):
    """
    Spark implementation for single imputation strategies.
    """

    def __init__(self,
                 impute_strategy: str,
                 column: Optional[Union[Iterable[str], str]] = None,
                 strategy_decider: Any = SingleImputationStrategyDecider,
                 fill_value: Optional[Any] = None,
                 strategy_params: Optional[Dict[str, Any]] = None):
        """
        Args:
            impute_strategy: The imputation strategy to use
            column: Column(s) to impute. If None, all columns with missing values
            strategy_decider: Strategy decision class for 'auto' mode
            fill_value: Fill value for constant strategy
            strategy_params: Additional parameters
        """
        self.impute_strategy = impute_strategy
        self.column = column
        self.fill_value = fill_value
        self.strategy_params = strategy_params or {}
        self.imputers: Dict[str, AHandler] = {}
        self._decider = strategy_decider()

        self._imputers_map = {
            "continuous": {
                "mean": SimpleImputerSpark,
                "median": SimpleImputerSpark,
                "most_frequent": SimpleImputerSpark,
                "constant": SimpleImputerSpark,
                "interpolate": LinearInterpolationImputerSpark,
                "backfill": DirectionFillImputerSpark,
                "forwardfill": DirectionFillImputerSpark
            },
            "categorical": {
                "most_frequent": SingleCategoricalImputerSpark,
                "constant": SingleCategoricalImputerSpark,
                "least_frequent": SingleCategoricalImputerSpark,
                "backfill": DirectionFillImputerSpark,
                "forwardfill": DirectionFillImputerSpark
            },
            "date": {
                "interpolate": LinearInterpolationImputerSpark,
                "backfill": DirectionFillImputerSpark,
                "forwardfill": DirectionFillImputerSpark
            }
        }

    def _get_missing_condition(self, df: SparkDataFrame, column_name: str):
        """Get condition for missing values (handles both null and 'NaN' string)"""
        col_obj = col(column_name)
        
        # Get column data type
        col_type = dict(df.dtypes)[column_name]
        
        if col_type in ['double', 'float', 'int', 'bigint', 'smallint', 'tinyint']:
            # For numeric columns, check both isNull and isnan
            return col_obj.isNull() | isnan(col_obj)
        else:
            # For string columns, check isNull and string representations
            return (col_obj.isNull() | 
                   (col_obj == "NaN") | 
                   (col_obj == "nan") | 
                   (col_obj == "null") |
                   (col_obj == ""))

    def fit(self, df: SparkDataFrame) -> "SingleImputationSpark":
        """Fit the imputers for each column"""
        
        # Determine which columns to impute
        if self.column is None:
            # Find all columns with missing values
            columns = []
            for col_name in df.columns:
                null_count = df.filter(self._get_missing_condition(df, col_name)).count()
                if null_count > 0:
                    columns.append(col_name)
        elif isinstance(self.column, str):
            columns = [self.column]
        else:
            columns = [col for col in self.column if col in df.columns]

        for col_name in columns:
            # Determine strategy if "auto"
            strategy = self.impute_strategy
            if strategy == "auto" or strategy is None:
                # Convert to pandas series for decision making (small sample)
                pandas_series = df.select(col_name).limit(1000).toPandas()[col_name]
                strategy = self._decider.decide_imputation_strategy(pandas_series)

            # Prepare strategy-specific parameters
            params = self.strategy_params.copy()
            params["strategy"] = strategy
            params["column"] = col_name
            if self.fill_value is not None:
                params["fill_value"] = self.fill_value

            # Determine feature type for Spark (simplified)
            col_type = dict(df.dtypes)[col_name]
            if col_type in ['double', 'float', 'int', 'bigint', 'smallint', 'tinyint']:
                feature_type = "continuous"
            elif col_type in ['timestamp', 'date']:
                feature_type = "date"
            else:
                feature_type = "categorical"

            # Get the appropriate imputer class
            imputer_class = self._imputers_map.get(feature_type, {}).get(strategy)
            if imputer_class is None:
                raise ValueError(f"Invalid imputation strategy '{strategy}' for {feature_type} feature type. "
                               f"Available strategies: {list(self._imputers_map[feature_type].keys())}")

            # Filter parameters for the imputer class
            filtered_params = Structs.filter_kwargs_for_class(imputer_class, params)
            
            # Initialize and fit the imputer
            self.imputers[col_name] = imputer_class(**filtered_params)
            self.imputers[col_name].fit(df)

        return self

    def transform(self, df: SparkDataFrame) -> SparkDataFrame:
        """Transform the DataFrame using fitted imputers"""
        
        if not self.imputers:
            raise RuntimeError("This SingleImputationSpark instance is not fitted yet. "
                             "Call 'fit' before calling 'transform'.")

        result_df = df
        for col_name, imputer in self.imputers.items():
            result_df = imputer.transform(result_df)

        return result_df

    def fit_transform(self, df: SparkDataFrame) -> SparkDataFrame:
        """Fit and transform in one step"""
        self.fit(df)
        return self.transform(df)
