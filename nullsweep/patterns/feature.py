import pandas as pd
from typing import Any, Dict, Tuple
from .mtype.mar_based import MarBasedDetection


class FeaturePatternManager:

    def __init__(self):
        """
        A class to manage and detect patterns in features using various approaches.
        
        Attributes:
            _decider (Dict[str, Any]): A dictionary mapping approach names to their corresponding classes.
        """
        self._decider: Dict[str, Any] = {
            "mar_based": MarBasedDetection
        }

    def detect_pattern(self, approach: str, method: str, df: pd.DataFrame, feature: str, *args, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Detects the pattern in the specified feature using the chosen approach and method.
        
        Args:
            approach (str): The approach to use for detection (e.g., "mar_based").
            method (str): The method to use within the approach (e.g., "logistic").
            df (pd.DataFrame): The DataFrame containing the data.
            feature (str): The feature/column to check for patterns.
            *args: Additional arguments to pass to the approach class.
            **kwargs: Additional keyword arguments to pass to the approach class.
        
        Returns:
            Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern and the detailed result.
        
        Raises:
            ValueError: If the specified approach is not supported.
        """
        if approach not in self._decider:
            raise ValueError(f"Unsupported approach '{approach}'. Supported approaches are: {list(self._decider.keys())}")
        
        decider = self._decider.get(approach)()
        pattern, data = decider.decide(method, df, feature, *args, **kwargs)

        return pattern, data