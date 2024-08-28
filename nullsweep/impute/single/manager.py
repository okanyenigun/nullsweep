import pandas as pd
from sklearn.impute import SimpleImputer
from typing import Union, Any, Dict, Optional
from .categorical import SingleCategoricalImputer
from .interpolate import LinearInterpolationImputer
from .direction import DirectionFillImputer
from .decision import SingleImputationStrategyDecider
from ...utils.structs import Structs


class SingleImputationManager:
    
    """
    A class to manage different imputation strategies for a single feature in a pandas DataFrame.
    """

    def __init__(self, strategy_decider: Any=SingleImputationStrategyDecider):
        """
        Initialize the manager with a strategy decider.

        Args:
            strategy_decider (Any): The strategy decider class or instance to use.
        """
        self.imputer = None
        self._decider = strategy_decider()
        self._imputers = {
            "continuous": {
                "mean": SimpleImputer,
                "median": SimpleImputer,
                "most_frequent": SimpleImputer,
                "constant": SimpleImputer,
                "interpolate": LinearInterpolationImputer,
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
                "interpolate": LinearInterpolationImputer,
                "backfill": DirectionFillImputer,
                "forwardfill": DirectionFillImputer,
            }
        }

    def impute_single_feature(self,
                              df: pd.DataFrame, 
                              feature: str, 
                              strategy: str, 
                              fill_value: Optional[Any], 
                              strategy_params: Optional[Dict[str, Any]]
                              ) -> pd.DataFrame:
        """
        Use the specified imputation strategy to impute missing values in the specified feature of the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            feature (str): The feature/column to impute missing values.
            strategy (str): The imputation strategy to use.
            fill_value (Optional[Any]): The value to use for constant imputation.
            strategy_params (Optional[Dict[str, Any]]): Additional parameters for the imputation strategy.
        
        Raises:
            ValueError: If the specified feature does not exist or the strategy is invalid.

        Returns:
            pd.DataFrame: The DataFrame with missing values imputed in the specified feature.
        """
        if feature not in df.columns:
            raise ValueError(f"Feature '{feature}' does not exist in the DataFrame.")
        
        series = df[feature]

        if series.isna().sum() == 0:
            return df  # No imputation needed if there are no missing values
        
        if strategy == "auto" or strategy is None:
            strategy = self._decider.decide_imputation_strategy(series)
        
        strategy_params = self._fix_strategy_params(strategy, fill_value, strategy_params)
        
        imputer = self._get_imputer(series, strategy_params)

        if isinstance(imputer, SimpleImputer):
            # SimpleImputer expects a 2D array, reshape the series
            series = series.values.reshape(-1, 1)

        df[feature] = imputer.fit_transform(series)

        self.imputer = imputer

        return df
    
    def _get_imputer(self, 
                     series: pd.Series, 
                     strategy_params: Optional[Dict[str, Any]]
                     ) -> Union[SimpleImputer, SingleCategoricalImputer, LinearInterpolationImputer, DirectionFillImputer]:
        """
        Get the imputer object based on the feature type and strategy.

        Args:
            series (pd.Series): The pandas Series to be imputed.
            strategy_params (Optional[Dict[str, Any]]): Additional parameters for the imputation strategy.

        Raises:
            ValueError: If the specified strategy is not valid for the feature type.

        Returns:
            Union[SimpleImputer, SingleCategoricalImputer, LinearInterpolationImputer, DirectionFillImputer]: The imputer object.
        """
        feature_type = Structs.detect_series_type(series)
        strategy = strategy_params.get("strategy")
        print(strategy_params)
        imputer = self._imputers.get(feature_type, {}).get(strategy)(**strategy_params)
        if imputer is None:
            raise ValueError(f"Invalid imputation strategy '{strategy}'. For {feature_type} type of features, the strategy must be one of: {list(self._imputers[feature_type].keys())}")
        
        return imputer
    
    def _fix_strategy_params(self, 
                             strategy: str, 
                             fill_value: Optional[Any], 
                             strategy_params: Optional[Dict[str, Any]]
                             ) -> Dict[str, Any]:
        """
        Fix the strategy parameters by adding the strategy and fill_value to the dictionary.

        Args:
            strategy (str): The imputation strategy to use.
            fill_value (Optional[Any]): The value to use for constant imputation.
            strategy_params (Optional[Dict[str, Any]]): Additional parameters for the imputation strategy.

        Returns:
            Dict[str, Any]: The updated strategy parameters.
        """
        if strategy_params is None:
            strategy_params = {}
        
        strategy_params["strategy"] = strategy
        if fill_value:
            strategy_params["fill_value"] = fill_value
        return strategy_params
    
    def get_imputer_object(self) -> Union[SimpleImputer, SingleCategoricalImputer, LinearInterpolationImputer, DirectionFillImputer]:
        """
        Get the imputer object used for the last imputation.

        Returns:
            Union[SimpleImputer, SingleCategoricalImputer, LinearInterpolationImputer, DirectionFillImputer]: The imputer object.
        """
        if self.imputer is None:
            raise ValueError("No imputer has been fitted yet.")
        return self.imputer