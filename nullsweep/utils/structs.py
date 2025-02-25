import inspect
import pandas as pd
import polars as pl
from typing import Type, Dict, Any


class Structs:
    """
    A class that contains utility functions
    """
    
    @staticmethod
    def detect_series_type(series: pd.Series) -> str:
        """
        Detects the type of a pandas Series as one of "continuous", "categorical", or "date".

        Args:
            series (pd.Series): The pandas Series to be analyzed.

        Returns:
            str: The type of the series - "continuous", "categorical", or "date".
        """
        if pd.api.types.is_datetime64_any_dtype(series) or pd.api.types.is_timedelta64_dtype(series):
            return "date"
        elif pd.api.types.is_numeric_dtype(series):
                return "continuous"
        else:
            return "categorical"
        
    @staticmethod
    def detect_series_type_polars(series: pl.Series) -> str:
        """
        Detects the type of a Polars Series as one of "continuous", "categorical", or "date".

        Args:
            series (pl.Series): The Polars Series to be analyzed.

        Returns:
            str: The type of the series - "continuous", "categorical", or "date".
        """
        dtype = series.dtype
        if dtype.is_temporal():
            return "date"
        elif dtype.is_numeric():
            return "continuous"
        elif dtype == pl.Categorical:
            return "categorical"
        else:
            return "categorical"
        
    @staticmethod
    def filter_kwargs_for_class(cls: Type, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters the input parameters to match the parameters of the specified class

        Args:
            cls (Type): The class to match the parameters against.
            params (Dict[str, Any]): The input parameters to be filtered.

        Returns:
            Dict[str, Any]: The filtered parameters that match the class parameters.
        """
        init_signature = inspect.signature(cls.__init__)

        init_params = {
            param_name
            for param_name, param in init_signature.parameters.items()
            if param_name != "self"
            }
        
        matched_params = {key: value for key, value in params.items() if key in init_params}
        
        return matched_params