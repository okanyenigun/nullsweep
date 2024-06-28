import pandas as pd
from typing import Any, Dict, Tuple
from .monotone.service import DataFramePatternDetector


class DatasetPatternManager:
    """
    A class to manage and detect patterns in datasets using various approaches.
    
    Attributes:
        _decider (Dict[str, Any]): A dictionary mapping approach names to their corresponding classes.
    """
    def __init__(self):
        self._decider = {
            "coarse": DataFramePatternDetector,
        }

    def detect_pattern(self, approach: str, df: pd.DataFrame, *args, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Detects the pattern in the dataset using the chosen approach.
        
        Args:
            approach (str): The approach to use for detection (e.g., "coarse").
            df (pd.DataFrame): The DataFrame containing the data.
            *args: Additional arguments to pass to the approach class.
            **kwargs: Additional keyword arguments to pass to the approach class.
        
        Returns:
            Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern and the detailed result.
        
        Raises:
            ValueError: If the specified approach is not supported.
        """
        if approach not in self._decider:
            raise ValueError(f"Unsupported approach '{approach}'. Supported approaches are: {list(self._decider.keys())}")

        decider = self._decider.get(approach)(df, *args, **kwargs)
        pattern, data = decider.detect_pattern()
        return pattern, data
    