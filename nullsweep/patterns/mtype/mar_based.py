import pandas as pd
from typing import Any, Dict, Tuple
from ..mar.logistic_regression import MARLogisticRegression


class MarBasedDetection:
    """
    A class to decide the missing data pattern detection method and determine the pattern.
    
    Attributes:
        _methods (Dict[str, Any]): A dictionary mapping method names to their corresponding classes.
    """

    def __init__(self):
        self._methods: Dict[str, Any] = {
            "logistic": MARLogisticRegression,
        }

    def decide(self, method: str, df: pd.DataFrame, feature: str, *args, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Decides the missing data pattern based on the specified method.
        
        Args:
            method (str): The method to use for detection (e.g., "logistic").
            df (pd.DataFrame): The DataFrame containing the data.
            feature (str): The feature/column to check for missing data patterns.
            *args: Additional arguments to pass to the method class.
            **kwargs: Additional keyword arguments to pass to the method class.
        
        Returns:
            Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern ("MAR" or "MCAR") and the detailed result.
        
        Raises:
            ValueError: If the specified method is not supported.
        """
        if method not in self._methods:
            raise ValueError(f"Unsupported method '{method}'. Supported methods are: {list(self._methods.keys())}")
        
        operator = self._methods.get(method)(df, feature, *args, **kwargs)
        flag, data = operator.detect_pattern()
        pattern = "MAR" if flag else "MCAR"
        
        return pattern, data