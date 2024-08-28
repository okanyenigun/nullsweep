import pandas as pd
from typing import Any, Dict, Tuple, Optional, Iterable, Union
from .patterns.df import DatasetPatternManager
from .patterns.feature import FeaturePatternManager
from .impute.single.manager import SingleImputationManager


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
                feature: Optional[Union[Iterable, str]], 
                strategy: str="auto",
                fill_value: Optional[Any]=None,
                strategy_params: Optional[Dict[str, Any]]=None,
                in_place: bool=True
                ) -> pd.DataFrame:
    """
    Impute missing values in a specific feature (column) of a DataFrame using a specified or automatically determined imputation strategy.

    This function provides a flexible and powerful way to handle missing data in a DataFrame by allowing the user to apply a variety of imputation strategies, including mean, median, most frequent, constant value, linear interpolation, and directional fills (forward/backward). The strategy can be manually specified or automatically decided based on the data characteristics. The function integrates seamlessly with pandas DataFrames, making it ideal for preprocessing steps in machine learning pipelines.

    Args:
        df (pd.DataFrame): 
            The DataFrame containing the data that requires imputation. This DataFrame should be in a tabular format with rows as observations and columns as features.
        
        feature (str): 
            The specific column within the DataFrame that contains missing values to be imputed. This must be the exact name of the column as a string.

        strategy (Optional[str]): 
            The imputation strategy to use. If not provided or set to "auto", the strategy is automatically determined based on the feature's data type and distribution.
            Possible values include:
            - "mean": Impute using the mean of the column (for continuous data).
            - "median": Impute using the median of the column (for continuous data).
            - "most_frequent": Impute using the most frequent value in the column.
            - "constant": Impute using a constant value provided in `fill_value`.
            - "interpolate": Impute using linear interpolation (for continuous or date data).
            - "forwardfill": Impute by propagating the last valid observation forward.
            - "backfill": Impute by propagating the next valid observation backward.
            If set to "auto", the strategy will be determined using the `SingleImputationStrategyDecider`.

        fill_value (Optional[Any]): 
            The value to use for constant imputation if `strategy` is set to "constant". This can be any scalar value appropriate for the data type of the feature.

        strategy_params (Optional[Dict[str, Any]]): 
            Additional parameters for the imputation strategy. These parameters are passed directly to the underlying imputation class (e.g., `SimpleImputer`, `SingleCategoricalImputer`, `LinearInterpolationImputer`, or `DirectionFillImputer`).
            Example parameters include:
            - "strategy": The imputation strategy to be applied (as described above).
            - "fill_value": A specific value for constant imputation.
            - Other method-specific parameters as required by the selected imputation technique.

    Returns:
        pd.DataFrame: 
            A modified DataFrame where the specified feature has had its missing values imputed according to the chosen strategy. The original DataFrame is returned with the imputed values in place, ensuring that no data outside the specified feature is altered.

    Raises:
        ValueError: 
            - If the specified feature does not exist in the DataFrame.
            - If the selected strategy is invalid or not applicable for the feature's data type.
            - If `fill_value` is required for the selected strategy but not provided.

        TypeError:
            - If the input `df` is not a pandas DataFrame.
            - If the `strategy_params` is not a dictionary, when provided.

    Example Usage:
    --------------
    ```python
    import pandas as pd
    from your_module_name import impute_single_feature

    # Sample DataFrame
    data = {
        'Age': [25, 30, np.nan, 35, 40],
        'Gender': ['Male', 'Female', np.nan, 'Female', 'Male']
    }
    df = pd.DataFrame(data)

    # Impute missing values in 'Age' using mean
    df = impute_single_feature(df, feature='Age', strategy='mean')

    # Impute missing values in 'Gender' using the most frequent value
    df = impute_single_feature(df, feature='Gender', strategy='most_frequent')

    # Impute missing values in 'Age' using linear interpolation
    df = impute_single_feature(df, feature='Age', strategy='interpolate')

    # Impute missing values for multiple features
    df = impute_single_feature(df, feature=['Age', 'Gender'], strategy='interpolate')

    # Impute all features with missing values using automatic strategy detection
    df = impute_single_feature(df)
    ```

    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input `df` must be a pandas DataFrame.")
    
    if not in_place:
        df = df.copy()

    manager = SingleImputationManager()

    if feature:
        if isinstance(feature, str):
            df = manager.impute_single_feature(df, feature, strategy, fill_value, strategy_params)
        elif isinstance(feature, Iterable):
            for f in feature:
                df = manager.impute_single_feature(df, f, strategy, fill_value, strategy_params)
    else:
        column_list = df.columns.tolist()
        for f in column_list:
            df = manager.impute_single_feature(df, f, strategy, fill_value, strategy_params)
    
    return df

