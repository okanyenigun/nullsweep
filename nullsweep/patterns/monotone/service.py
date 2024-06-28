import itertools
import pandas as pd
from typing import Any, Dict, Tuple, Union


class DataFramePatternDetector:
    """
    A class to detect patterns of missing data in a DataFrame.
    
    Attributes:
        df (pd.DataFrame): The DataFrame containing the data.
    """

    def __init__(self, df: pd.DataFrame):
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
    
    def detect_univariate(self) -> Union[str, None]:
        """
        Detects if there is a univariate pattern of missing data.
        
        Returns:
            Union[str, None]: The column with univariate missing pattern or None if no such pattern is found.
        """
        missing_counts = self.df.isna().sum()

        for col, count in missing_counts.items():
            if count > 0 and (missing_counts.drop(col) == 0).all():
                return col
        return None
    
    def detect_monotone(self) -> Tuple[bool, pd.DataFrame]:
        """
        Detects if there is a monotone pattern of missing data.
        
        Returns:
            Tuple[bool, pd.DataFrame]: A boolean indicating if a monotone pattern is found and the corresponding monotone matrix.
        """
        df_na = self.df.isna()
        columns_with_missing = [col for col in df_na.columns if df_na[col].any()]
        
        if not columns_with_missing:
            return False, pd.DataFrame()
        
        column_pairs = list(itertools.permutations(columns_with_missing, 2))
        monotone_matrix = pd.DataFrame(False, index=columns_with_missing, columns=columns_with_missing)
        
        for col1, col2 in column_pairs:
            if (df_na[col2] | ~df_na[col1]).all():
                monotone_matrix.loc[col1, col2] = True
        
        monotone = monotone_matrix.any().any()
        return monotone, monotone_matrix
