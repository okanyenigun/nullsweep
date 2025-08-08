import itertools
import pandas as pd
from typing import Tuple, Union
from .base import ADataFramePatternDetector

try:
    from pyspark.sql import DataFrame as SparkDataFrame
    from pyspark.sql.functions import col, isnan, isnull, when, count, sum as spark_sum
    SPARK_AVAILABLE = True
except ImportError:
    SparkDataFrame = None
    SPARK_AVAILABLE = False


class SparkDFPatternDetector(ADataFramePatternDetector):
    """
    PySpark DataFrame pattern detector for missing data patterns.
    """

    def detect_univariate(self) -> Union[str, None]:
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")

        # Count missing values per column
        missing_counts = {}
        for column in self.df.columns:
            missing_count = self.df.filter(
                col(column).isNull() | isnan(col(column))).count()
            missing_counts[column] = missing_count

        # Check for univariate pattern
        for col_name, count in missing_counts.items():
            if count > 0:
                # Check if all other columns have zero missing values
                others_zero = all(missing_counts[other_col] == 0
                                  for other_col in missing_counts.keys()
                                  if other_col != col_name)
                if others_zero:
                    return col_name
        return None

    def detect_monotone(self) -> Tuple[bool, pd.DataFrame]:
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")

        # Create boolean DataFrame for missing values
        missing_df = self.df.select([
            (col(c).isNull() | isnan(col(c))).alias(c)
            for c in self.df.columns
        ])

        # Find columns with any missing values
        cols_with_na = []
        for column in self.df.columns:
            has_missing = missing_df.filter(col(column) == True).count() > 0
            if has_missing:
                cols_with_na.append(column)

        if not cols_with_na:
            return False, pd.DataFrame()

        # Create monotone matrix
        monotone_matrix = pd.DataFrame(
            False, index=cols_with_na, columns=cols_with_na)

        # Check monotonicity for each pair of columns
        for col1, col2 in itertools.permutations(cols_with_na, 2):
            # Condition: wherever col2 is missing, col1 must also be missing
            # This means: col2_missing OR NOT col1_missing should always be true
            condition_df = missing_df.select(
                (col(col2) | (~col(col1))).alias("condition")
            )

            # Check if condition is true for all rows
            false_count = condition_df.filter(
                col("condition") == False).count()
            is_monotone = (false_count == 0)

            if is_monotone:
                monotone_matrix.loc[col1, col2] = True

        # Check if any monotone pattern exists
        has_monotone = monotone_matrix.values.any()
        return has_monotone, monotone_matrix
