import itertools
import pandas as pd
from typing import Tuple, Union
from .base import ADataFramePatternDetector


class PandasDFPatternDetector(ADataFramePatternDetector):

    def detect_univariate(self) -> Union[str, None]:
        missing_counts = self.df.isna().sum()

        for col, count in missing_counts.items():
            if count > 0 and (missing_counts.drop(col) == 0).all():
                return col
        return None
    
    def detect_monotone(self) -> Tuple[bool, pd.DataFrame]:
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
