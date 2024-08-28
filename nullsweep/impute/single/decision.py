import pandas as pd
import numpy as np
from scipy.stats import skew, shapiro
from typing import Dict, Any, Optional
from ...utils.structs import Structs


class SingleImputationStrategyDecider:

    def __init__(self, thresholds: Optional[Dict[str, Any]]=None):
        self._default_thresholds = {
            "skewness": 0.5,
            "shapiro_p_value": 0.05,
            "sporadic": 0.2
        }
        self._thresholds = thresholds if thresholds else self._default_thresholds

    def decide_imputation_strategy(self, series: pd.Series) -> str:
        """
        Decides the imputation strategy for a given pandas Series

        Args:
            series (pd.Series): The pandas Series to be analyzed.

        Returns:
            str: The imputation strategy to be used.
        """

        feature_type = Structs.detect_series_type(series)

        if feature_type == "continuous":
            return self._decide_continuous_imputation(series)
        elif feature_type == "categorical":
            return "most_frequent"
        elif feature_type == "date":
            return "interpolate"
        return
    
    def _decide_continuous_imputation(self, series: pd.Series) -> str:
        """
        Decides whether to use mean, median, or linear interpolation based on the distribution of the data.
        
        Args:
            series (pd.Series): The pandas Series to analyze.

        Returns:
            str: 'mean', 'median', or 'interpolate' based on the analysis.
        """
        # Convert to pandas Series if input is a NumPy array
        if isinstance(series, np.ndarray):
            series = pd.Series(series.flatten())

        if self._is_time_series(series) and self._has_sporadic_missing_values(series):
            return "interpolate"
        
        series_skewness = skew(series.dropna())
        shapiro_test = shapiro(series.dropna())
        p_value = shapiro_test.pvalue
        
        skewness_threshold = self._thresholds["skewness"]
        p_value_threshold = self._thresholds["shapiro_p_value"]

        if abs(series_skewness) < skewness_threshold and p_value > p_value_threshold:
            return "mean"
        else:
            return "median"
        
    def _is_time_series(self, series: pd.Series) -> bool:
        """
        Checks if the series is a time series or has a natural ordering.
        
        Args:
            series (pd.Series): The pandas Series to analyze.
        
        Returns:
            bool: True if the series is a time series, False otherwise.
        """
        return pd.api.types.is_datetime64_any_dtype(series.index) or series.index.is_monotonic_increasing
    
    def _has_sporadic_missing_values(self, series: pd.Series) -> bool:
        """
        Checks if the missing values in the series are sporadic.
        
        Args:
            series (pd.Series): The pandas Series to analyze.
        
        Returns:
            bool: True if missing values are sporadic, False if they are clustered or numerous.
        """
        missing_ratio = series.isna().mean()  
        sparsity_threshold = self._thresholds["sporadic"]
        return missing_ratio < sparsity_threshold