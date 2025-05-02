import itertools
import polars as pl
from typing import Optional, Tuple
from .base import ADataFramePatternDetector


class PolarsDFPatternDetector(ADataFramePatternDetector):

    def detect_univariate(self) -> Optional[str]:
        missing_counts = self.df.null_count()
        
        for col in missing_counts.columns:
            count = missing_counts[col][0]

            if count > 0 and missing_counts.select([pl.col(c) for c in missing_counts.columns if c != col]).sum().row(0) == (0,) * (len(missing_counts.columns) - 1):
                return col
        return None
    
    def detect_monotone(self) -> Tuple[bool, pl.DataFrame]:
        df_na_pl = self.df.select([
            pl.col(c).is_null().alias(c) for c in self.df.columns
        ])
        
        columns_with_missing = [
            c for c in df_na_pl.columns
            if df_na_pl.select(pl.col(c).sum()).to_series()[0] > 0
        ]

        n = len(columns_with_missing)
        monotone_dict = {c: [False]*n for c in columns_with_missing}

        for i, col1 in enumerate(columns_with_missing):
            for j, col2 in enumerate(columns_with_missing):
                if col1 == col2:
                    continue

                is_monotone = df_na_pl.select(
                    (pl.col(col2) | ~pl.col(col1)).all().alias("m")
                ).to_series()[0]
                monotone_dict[col1][j] = bool(is_monotone)

        monotone_matrix_pl = pl.DataFrame(monotone_dict)

        monotone_property = any(
            any(row) for row in monotone_dict.values()
        )

        return monotone_property, monotone_matrix_pl