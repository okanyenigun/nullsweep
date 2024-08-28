import pandas as pd


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