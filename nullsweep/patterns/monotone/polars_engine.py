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
        df_na = self.df.select([
            pl.col(col).is_null().alias(col) for col in self.df.columns
        ])
        
        columns_with_missing = [
            col for col in self.df.columns 
            if df_na.select(pl.col(col)).sum()[0, 0] > 0
        ]
        
        if not columns_with_missing:
            return False, pl.DataFrame()
        
        column_pairs = list(itertools.permutations(columns_with_missing, 2))
        
        monotone_matrix = pl.DataFrame(
            {col: [False] * len(columns_with_missing) for col in columns_with_missing},
            schema={col: pl.Boolean for col in columns_with_missing}
        )
        monotone_matrix = monotone_matrix.with_columns(
            pl.Series(name="index", values=columns_with_missing)
        )
        
        for col1, col2 in column_pairs:
            is_monotone = df_na.select(
                (pl.col(col2) | ~pl.col(col1)).all()
            )[0, 0]
            
            if is_monotone:
                monotone_matrix = monotone_matrix.with_columns(
                    pl.when(pl.col("index") == col1)
                    .then(pl.lit(True))
                    .otherwise(pl.col(col2))
                    .alias(col2)
                )
        
        monotone = monotone_matrix.select(
            pl.exclude("index")
        ).select(pl.all().any()).select(pl.all().any())[0, 0]
        
        monotone_matrix = monotone_matrix.drop("index")
        
        return monotone, monotone_matrix