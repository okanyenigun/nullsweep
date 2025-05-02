import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
from typing import Any, Dict, Tuple, Optional, Iterable, Union, Literal
from .patterns.df import DatasetPatternManager
from .patterns.feature import FeaturePatternManager
from .visualization.funcs import PLOT_FUNCTIONS
from .router import ImputeFactory
from .config import DataType


GLOBAL_PATTERN_DETECTION_APPROACH = "coarse"
FEATURE_PATTERN_DETECT_APPROACH = "mar_based"
MAR_BASED_PATTERN_DETECT_METHOD = "logistic"


def detect_global_pattern(df: DataType) -> Tuple[str, Dict[str, Any]]:
    """
    Detects the global pattern of missing data in the DataFrame.

    Args:
        df (DataType): The DataFrame containing the data.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern and the detailed result.

    Raises:
        TypeError: If the input 'df' is not a DataType.
        ValueError: If the input DataFrame is empty.
    """
    if not isinstance(df, DataType):
        raise TypeError(f"Unsupported data type. Please provide a pandas, or Polars DataFrame, or Dask DataFrame. Sent: {type(df)}")

    manager = DatasetPatternManager()
    pattern, data = manager.detect_pattern(GLOBAL_PATTERN_DETECTION_APPROACH, df)
    return pattern, data


def detect_feature_pattern(df: DataType, feature_name: str) -> Tuple[str, Dict[str, Any]]:
    """
    Detects the pattern of missing data in the specified feature of the DataFrame.

    Args:
        df (DataType): The DataFrame containing the data.
        feature_name (str): The feature/column to check for patterns.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern and the detailed result.

    Raises:
        TypeError: If the input 'df' is not a DataType.
        ValueError: If the specified feature is not found in the DataFrame columns.
    """
    if not isinstance(df, DataType):
        raise TypeError("The input 'df' must be a pandas or Polars DataFrame, or Dask DataFrame.")
    
    if feature_name not in df.columns:
        raise ValueError(f"The specified feature '{feature_name}' is not found in the DataFrame columns. Please provide a valid feature name.")
    
    manager = FeaturePatternManager()
    pattern, data = manager.detect_pattern(FEATURE_PATTERN_DETECT_APPROACH, MAR_BASED_PATTERN_DETECT_METHOD, df, feature_name)
    return pattern, data


def impute_nulls(
        df: DataType, 
        column: Optional[Union[Iterable, str]] = None, 
        strategy: str = "auto",
        fill_value: Optional[Any] = None,
        strategy_params: Optional[Dict[str, Any]] = None,
        in_place: bool = False,
        **kwargs
        ) -> pd.DataFrame:
    """
    Impute missing values in a DataFrame using a specified strategy or an automated decision-making process.

    This function provides a unified interface for handling missing values across a DataFrame. 
    It dynamically routes to the appropriate imputation handler based on the provided strategy and column type.
    It supports a wide variety of imputation techniques, including statistical, directional, categorical, 
    and interpolation-based methods.

    Args:
        df (DataType): 
            The input pandas DataFrame to process.
        column (Optional[Union[Iterable, str]]): 
            The target column(s) to apply the imputation on. Can be a single column name (str), 
            a list of column names (Iterable), or None. If None, all columns with missing values 
            are considered.
        strategy (str): 
            The imputation strategy to use. Supports a variety of strategies, including:
            - For continuous features: "mean", "median", "most_frequent", "constant", 
              "interpolate", "backfill", "forwardfill".
            - For categorical features: "most_frequent", "constant", 
              "backfill", "forwardfill".
            - For date features: "interpolate", "backfill"
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
        TypeError: If `df` is not a DataType.
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

    if not isinstance(df, DataType):
        raise TypeError("Input `df` must be a pandas or polars DataFrame, or Dask DataFrame.")
    
    if not in_place:
        df = deepcopy(df)

    data_engine = df.__module__.split(".")[0]

    factory = ImputeFactory()
    operator = factory.create_imputer(strategy, data_engine, column, fill_value, strategy_params, **kwargs)

    df = operator.fit_transform(df)

    return df


def plot_missing_values(
        df: pd.DataFrame,
        plot_type: Literal['heatmap', 'correlation', 'percentage', 'matrix', 'dendogram', 
                           'upset_plot', 'pair', 'wordcloud', 'histogram'],
        **kwargs
        ) -> None:
    """
    Visualize missing values in a DataFrame using various plot types.

    This function provides an interface to visualize missing data in a DataFrame through a variety of customizable plots, 
    including heatmaps, correlation maps, bar charts, and more. Each plot type highlights missing data patterns to 
    facilitate understanding and decision-making regarding data cleaning and preprocessing.

    Args:
        df (pd.DataFrame):
            The input DataFrame containing the data to analyze for missing values.
        plot_type (Literal):
            The type of plot to generate. Options include:

            - 'heatmap': Visualize missing data using a heatmap.
            - 'correlation': Show correlations between missing data in different columns.
            - 'percentage': Display the percentage of missing values per column as a bar chart.
            - 'matrix': Visualize the missing data structure with a matrix plot.
            - 'dendogram': Use a dendrogram to highlight clustering of missingness patterns.
            - 'upset_plot': Display intersections of missing data patterns as an upset plot.
            - 'pair': Create a pair plot that incorporates missing data patterns.
            - 'wordcloud': Visualize missing data proportions as a word cloud of column names.
            - 'histogram': Plot a histogram of the number of missing values per row.
        **kwargs:
            Additional keyword arguments to pass to the underlying plot function, if applicable.

    Raises:
        ValueError: If an invalid plot_type is provided.

    Returns:
        None

    Examples:
        >>> plot_missing_values(df, plot_type='heatmap')
        >>> plot_missing_values(df, plot_type='percentage')
    """
    
    if plot_type in PLOT_FUNCTIONS:
        fig = PLOT_FUNCTIONS[plot_type](df, **kwargs)
        plt.close(fig)
    else:
        raise ValueError(f"Invalid plot_type '{plot_type}'. Choose from {list(PLOT_FUNCTIONS.keys())}.")

    return fig

