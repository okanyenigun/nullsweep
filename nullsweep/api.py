import pandas as pd
from typing import Any, Dict, Tuple, Optional, Iterable, Union
from .patterns.df import DatasetPatternManager
from .patterns.feature import FeaturePatternManager
from .router import HandlingRouter


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


def impute_nulls(df: pd.DataFrame, 
                column: Optional[Union[Iterable, str]] = None, 
                strategy: str = "auto",
                fill_value: Optional[Any] = None,
                strategy_params: Optional[Dict[str, Any]] = None,
                in_place: bool = True,
                **kwargs
                ) -> pd.DataFrame:
    """
    Impute missing values in a DataFrame using a specified strategy or an automated decision-making process.

    This function provides a unified interface for handling missing values across a DataFrame. 
    It dynamically routes to the appropriate imputation handler based on the provided strategy and column type.
    It supports a wide variety of imputation techniques, including statistical, directional, categorical, 
    and interpolation-based methods.

    Args:
        df (pd.DataFrame): 
            The input pandas DataFrame to process. Must not be empty.
        column (Optional[Union[Iterable, str]]): 
            The target column(s) to apply the imputation on. Can be a single column name (str), 
            a list of column names (Iterable), or None. If None, all columns with missing values 
            are considered.
        strategy (str): 
            The imputation strategy to use. Supports a variety of strategies, including:
            - For continuous features: "mean", "median", "most_frequent", "constant", 
              "interpolate", "backfill", "forwardfill".
            - For categorical features: "most_frequent", "constant", "least_frequent", 
              "backfill", "forwardfill".
            - For date features: "interpolate", "backfill", "forwardfill".
            - "auto": Automatically decides the best strategy based on the data.
        fill_value (Optional[Any]): 
            The value to use for imputation when the strategy is "constant".
        strategy_params (Optional[Dict[str, Any]]): 
            Additional parameters to configure the imputation strategy. Examples include 
            interpolation methods for "interpolate" or estimator parameters for regression-based 
            strategies.
        in_place (bool): 
            Whether to modify the input DataFrame in place. Defaults to True. If False, 
            a copy of the DataFrame is created and returned.
        **kwargs: 
            Additional arguments for the underlying imputation handlers. This may include 
            handler-specific parameters or deprecated arguments (e.g., `feature`).

    Returns:
        pd.DataFrame: 
            The DataFrame with missing values imputed according to the specified strategy.

    Raises:
        TypeError: If `df` is not a pandas DataFrame.
        ValueError: If `df` is empty or if no columns contain missing values.
        RuntimeError: If no suitable handler is found for the specified strategy or column type.

    Notes:
        - If `column` is None, the function will identify all columns with missing values 
          and apply the imputation strategy to them.
        - The "auto" strategy leverages the `SingleImputationStrategyDecider` to select 
          the most appropriate imputation method dynamically.
        - The "in_place" parameter determines whether the original DataFrame is modified 
          or a new DataFrame is returned.
        - If the deprecated `feature` argument is provided, it will be treated as `column` 
          with a warning.

    Examples:
        Basic usage with a single column:
        >>> df = pd.DataFrame({'A': [1, None, 3], 'B': [4, None, 6]})
        >>> impute_nulls(df, column='A', strategy='mean')

        Imputation with multiple columns:
        >>> impute_nulls(df, column=['A', 'B'], strategy='most_frequent')

        Using a constant fill value:
        >>> impute_nulls(df, column='A', strategy='constant', fill_value=0)

        Automatic strategy selection:
        >>> impute_nulls(df, strategy='auto')

        Working with a copy of the DataFrame:
        >>> df_copy = impute_nulls(df, column='A', strategy='mean', in_place=False)
    """

    if "feature" in kwargs:
        print("Warning! The 'feature' argument is deprecated. Please use 'column' instead.")
        column = column if column else kwargs.get("feature", None)

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input `df` must be a pandas DataFrame.")
    
    if df.empty:
        raise ValueError("Input DataFrame is empty. Please provide a DataFrame with data.")
    
    if not in_place:
        df = df.copy()

    router = HandlingRouter()

    operator = router.route(strategy, column, fill_value, strategy_params, **kwargs)

    df = operator.fit_transform(df)

    return df
   