from typing import Optional, Union, Iterable
from ...bases.handler import AHandler

try:
    from pyspark.sql.functions import col, isnan, when
    SPARK_AVAILABLE = True
except ImportError:
    SparkDataFrame = None
    SPARK_AVAILABLE = False


class MissingIndicatorSpark(AHandler):
    """
    A class to generate a binary indicator column for missing values
    in a specified column for PySpark DataFrames.
    """

    def __init__(self, column: Optional[Union[Iterable, str]]=None, indicator_column_suffix: str = "_missing"):
        """
        Args:
            column (Optional[Union[Iterable, str]], optional): given column(s) to generate the indicator column for. 
                If None, all columns in the DataFrame will be used. Defaults to None.
            indicator_column_suffix (str, optional): The suffix to append to the column name to generate the 
                indicator column name. Defaults to "_missing".
        """
        if not isinstance(indicator_column_suffix, str):
            raise TypeError("Indicator column suffix must be a string.")
        
        self.column = column
        self.indicator_column_suffix = indicator_column_suffix
        self.indicator_column_names = None
        self.columns_to_process = None

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

    def fit(self, df) -> 'MissingIndicatorSpark':
        """
        Fit the missing indicator to the DataFrame.

        Args:
            df: The PySpark DataFrame to fit the handler to.

        Returns:
            MissingIndicatorSpark: Self for method chaining.
        """
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")

        if self.column is None:
            self.columns_to_process = df.columns
        elif isinstance(self.column, str):
            self.columns_to_process = [self.column]
        else:
            self.columns_to_process = list(self.column)
        
        # Check if the target column(s) are in the DataFrame
        missing_columns = [col for col in self.columns_to_process if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Target column(s) {missing_columns} not found in the DataFrame.")

        # Determine the name for the indicator columns
        self.indicator_column_names = [
            f"{col}{self.indicator_column_suffix}" for col in self.columns_to_process
        ]

        return self

    def transform(self, df):
        """
        Transform the DataFrame by adding binary indicator columns for missing values.

        Args:
            df: The PySpark DataFrame to transform.

        Returns:
            DataFrame: The transformed PySpark DataFrame with indicator columns added.
        """
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")
            
        if self.indicator_column_names is None:
            raise ValueError("The MissingIndicator has not been fitted yet. Call 'fit' first.")

        # Add indicator columns for each specified column
        result_df = df
        for col_name, indicator_name in zip(self.columns_to_process, self.indicator_column_names):
            missing_condition = self._get_missing_condition(df, col_name)
            result_df = result_df.withColumn(
                indicator_name, 
                when(missing_condition, 1).otherwise(0)
            )
            
        return result_df
