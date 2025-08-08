from typing import List, Union, Optional
from ...bases.handler import AHandler

try:
    from pyspark.sql.functions import col, isnan
    SPARK_AVAILABLE = True
except ImportError:
    SparkDataFrame = None
    SPARK_AVAILABLE = False


class ColumnDeleterSpark(AHandler):
    """
    A class to delete columns from a PySpark DataFrame.
    """
    def __init__(self, column: Optional[Union[str, List[str]]]=None):
        self.columns = column
        self.columns_to_delete = None

    def _is_numeric_column(self, df, column_name: str) -> bool:
        """Check if a column is numeric type."""
        column_type = dict(df.dtypes)[column_name]
        numeric_types = ['int', 'bigint', 'float', 'double', 'decimal']
        return any(numeric_type in column_type.lower() for numeric_type in numeric_types)

    def _get_missing_condition(self, df, column_name: str):
        """Get the appropriate missing value condition based on column type."""
        if self._is_numeric_column(df, column_name):
            return col(column_name).isNull() | isnan(col(column_name))
        else:
            # For string columns, also check for common string representations of missing values
            return (col(column_name).isNull() | 
                   (col(column_name) == "") | 
                   (col(column_name) == "NaN") | 
                   (col(column_name) == "nan") |
                   (col(column_name) == "null") |
                   (col(column_name) == "NULL"))

    def fit(self, df) -> 'ColumnDeleterSpark':
        """
        Fit the column deleter to the DataFrame.

        Args:
            df: The PySpark DataFrame to fit the handler to.

        Returns:
            ColumnDeleterSpark: Self for method chaining.
        """
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")

        if self.columns is None:
            # Find columns with any missing values
            self.columns_to_delete = []
            for column in df.columns:
                missing_condition = self._get_missing_condition(df, column)
                has_missing = df.filter(missing_condition).count() > 0
                if has_missing:
                    self.columns_to_delete.append(column)
        else:
            if isinstance(self.columns, str):
                self.columns = [self.columns]
            self.columns_to_delete = [col for col in self.columns if col in df.columns]

            if not self.columns_to_delete:
                raise ValueError(
                    f"None of the specified columns {self.columns} exist in the DataFrame."
                )
        
        return self
    
    def transform(self, df):
        """
        Transform the DataFrame by dropping the specified columns.

        Args:
            df: The PySpark DataFrame to transform.

        Returns:
            DataFrame: The transformed PySpark DataFrame with columns removed.
        """
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")
            
        if self.columns_to_delete:
            return df.drop(*self.columns_to_delete)
        else:
            raise ValueError(
                "No columns to delete. Please ensure the `fit` method has been called successfully."
            )
