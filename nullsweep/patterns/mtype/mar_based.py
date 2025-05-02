from typing import Any, Dict, Tuple
from ..mar.polars_lr import MarLRPolars
from ..mar.pandas_lr import MarLRPandas
from ..mar.dask_lr import MarLRDask
from ...config import DataType


class MarBasedDetection:
    """
    A class to decide the missing data pattern detection method and determine the pattern.
    
    Attributes:
        _methods (Dict[str, Dict[str, MarTypeLogisticDetector]]): A dictionary mapping method names to their corresponding classes.
    """

    def __init__(self):
        self._methods: Dict[str, Any] = {
            "logistic": {
                "pandas": MarLRPandas,
                "polars": MarLRPolars,
                "dask": MarLRDask,
            },
        }

    def decide(self, method: str, df: DataType, feature: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Decides the missing data pattern based on the specified method.
        
        Args:
            method (str): The method to use for detection (e.g., "logistic").
            df (DataType): The DataFrame containing the data.
            feature (str): The feature/column to check for missing data patterns.
            **kwargs: Additional keyword arguments to pass to the method class.
        
        Returns:
            Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern ("MAR" or "MCAR") and the detailed result.
        
        Raises:
            ValueError: If the specified method is not supported.
        """
        if method not in self._methods:
            raise ValueError(f"Unsupported method '{method}'. Supported methods are: {list(self._methods.keys())}")
        
        engine = df.__module__.split(".")[0]

        if engine not in self._methods.get(method):
            raise ValueError(f"Unsupported engine '{engine}' for method '{method}'." 
                             f"Supported engines are: {list(self._methods.get(method).keys())}")
        
        service_instance = self._methods.get(method).get(engine)
        service = service_instance(df, feature, **kwargs)

        flag, data = service.detect_pattern()
        
        pattern = "MAR" if flag else "MCAR"
        
        return pattern, data