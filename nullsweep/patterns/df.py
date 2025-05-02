from typing import Any, Dict, Tuple
from .monotone.pandas_engine import PandasDFPatternDetector
from .monotone.polars_engine import PolarsDFPatternDetector
from .monotone.dask_engine import DaskDFPatternDetector
from ..config import DataType


class DatasetPatternManager:
    """
    A class to manage and detect patterns in datasets using various approaches.
    
    Attributes:
        _decider (Dict[str, Dict[str, ADataFramePatternDetector]]): A dictionary mapping approach names to their corresponding classes.
    """
    def __init__(self):
        self._decider = {
            "coarse": {
                "pandas": PandasDFPatternDetector,
                "polars": PolarsDFPatternDetector,
                "dask": DaskDFPatternDetector,
            }
        }

    def detect_pattern(self, approach: str, df: DataType, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Detects the pattern in the dataset using the chosen approach.
        
        Args:
            approach (str): The approach to use for detection (e.g., "coarse").
            df (DataType): The DataFrame containing the data.
            **kwargs: Additional keyword arguments to pass to the approach class.
        
        Returns:
            Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern and the detailed result.
        
        Raises:
            ValueError: If the specified approach is not supported.
        """
        engine = df.__module__.split(".")[0]

        if approach not in self._decider:
            raise ValueError(f"Unsupported approach '{approach}'. Supported approaches are: {list(self._decider.keys())}")

        service_instance = self._decider.get(approach).get(engine)

        if service_instance is None:
            raise ValueError(f"Unsupported engine '{engine}' for approach '{approach}'" 
                             f"Supported engines are: {list(self._decider.get(approach).keys())}")
        
        service = service_instance(df, **kwargs)
        pattern, data = service.detect_pattern()

        return pattern, data
    