from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Union
from ...config import DataType


class ADataFramePatternDetector(ABC):
    """
    Abstract class to detect patterns of missing data in a DataFrame.
    
    Attributes:
        df (DataType): The DataFrame containing the data.
    """

    def __init__(self, df: DataType):
        self.df = df

    def detect_pattern(self) -> Tuple[str, Dict[str, Any]]:
        """
        Detects the overall pattern of missing data in the DataFrame.
        
        Returns:
            Tuple[str, Dict[str, Any]]: A tuple containing the detected pattern type and details.
        """
        univariate = self.detect_univariate()
        if univariate:
            return "univariate", {"column": univariate}
        
        monotone, monotone_matrix = self.detect_monotone()
        if monotone:
            return "monotone", {"matrix": monotone_matrix}

        return "non-monotone", {}
    
    @abstractmethod
    def detect_univariate(self) -> Union[str, None]:
        """
        Detects if there is a univariate pattern of missing data.
        
        Returns:
            Union[str, None]: The column with univariate missing pattern or None if no such pattern is found.
        """
        pass

    @abstractmethod
    def detect_monotone(self) -> Tuple[bool, DataType]:
        """
        Detects if there is a monotone pattern of missing data.
        
        Returns:
            Tuple[bool, DataType]: A boolean indicating if a monotone pattern is found and the corresponding monotone matrix.
        """
        pass