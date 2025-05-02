import itertools
import pandas as pd
import dask.dataframe as dd
from typing import Tuple, Union
from .base import ADataFramePatternDetector


class DaskDFPatternDetector(ADataFramePatternDetector):

    def detect_univariate(self) -> Union[str, None]:
        # 1) Count missing per column (yields a pandas Series after compute)
        missing_counts: pd.Series = self.df.isna().sum().compute()

        # 2) Look for a column whose only missing values are in itself
        for col, count in missing_counts.items():
            others_zero = (missing_counts.drop(col) == 0).all()
            if count > 0 and others_zero:
                return col
        return None
    
    def detect_monotone(self) -> Tuple[bool, pd.DataFrame]:
        # 1) Create a lazy boolean mask of missingness
        df_na: dd.DataFrame = self.df.isna()

        # 2) Find which columns have any missing values
        missing_any: pd.Series = df_na.any().compute()
        cols_with_na = [c for c, has in missing_any.items() if has]

        if not cols_with_na:
            return False, pd.DataFrame()

        # 3) Prepare the result matrix as a small pandas DataFrame
        monotone_matrix = pd.DataFrame(False, index=cols_with_na, columns=cols_with_na)

        # 4) For each ordered pair, check monotonicity via lazy ops + compute()
        for col1, col2 in itertools.permutations(cols_with_na, 2):
            # condition: wherever col2 is missing, col1 must also be missing
            is_monotone = ( (df_na[col2] | (~df_na[col1]))  # lazy Series
                            .all()                            # lazy scalar
                            .compute() )                     # boolean
            if is_monotone:
                monotone_matrix.loc[col1, col2] = True

        # 5) Any True in the matrix means we have a monotone pattern
        has_monotone = monotone_matrix.values.any()
        return has_monotone, monotone_matrix