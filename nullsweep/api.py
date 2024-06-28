import pandas as pd
from typing import Any, Dict, Tuple
from .patterns.df import DatasetPatternManager
from .patterns.feature import FeaturePatternManager


GLOBAL_PATTERN_DETECTION_APPROACH = "coarse"
FEATURE_PATTERN_DETECT_APPROACH = "mar_based"
MAR_BASED_PATTERN_DETECT_METHOD = "logistic"


def detect_global_pattern(df: pd.DataFrame) -> Tuple[str, Dict[str, Any]]:
    """
    Detects the global pattern of missing data in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern and the detailed result.

    Raises:
        TypeError: If the input 'df' is not a pandas DataFrame.
        ValueError: If the input DataFrame is empty.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The input 'df' must be a pandas DataFrame.")
    
    if df.empty:
        raise ValueError("The input DataFrame is empty. Please provide a DataFrame with data.")
    
    manager = DatasetPatternManager()
    pattern, data = manager.detect_pattern(GLOBAL_PATTERN_DETECTION_APPROACH, df)
    return pattern, data


def detect_feature_pattern(df: pd.DataFrame, feature_name: str) -> Tuple[str, Dict[str, Any]]:
    """
    Detects the pattern of missing data in the specified feature of the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        feature_name (str): The feature/column to check for patterns.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern and the detailed result.

    Raises:
        TypeError: If the input 'df' is not a pandas DataFrame.
        ValueError: If the input DataFrame is empty.
        ValueError: If the specified feature is not found in the DataFrame columns.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("The input 'df' must be a pandas DataFrame.")
    
    if df.empty:
        raise ValueError("The input DataFrame is empty. Please provide a DataFrame with data.")
    
    if feature_name not in df.columns:
        raise ValueError(f"The specified feature '{feature_name}' is not found in the DataFrame columns. Please provide a valid feature name.")
    
    manager = FeaturePatternManager()
    pattern, data = manager.detect_pattern(FEATURE_PATTERN_DETECT_APPROACH, MAR_BASED_PATTERN_DETECT_METHOD, df, feature_name)
    return pattern, data
