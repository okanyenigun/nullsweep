from typing import Union, Optional, List
from ...bases.handler import AHandler

try:
    from pyspark.sql.functions import col, isnan, when, lit
    SPARK_AVAILABLE = True
except ImportError:
    SparkDataFrame = None
    SPARK_AVAILABLE = False


class ListWiseDeleterSpark(AHandler):
    """
    A class to delete rows from a PySpark DataFrame based on the number of missing values in each row.
    """

    def __init__(self, threshold: Union[float, int]=0.5, column: Optional[Union[str, List[str]]]=None):
        """
        Args:
            threshold (Union[float, int], optional): The threshold for the number of missing values in each row. 
                If an integer, the row will be deleted if it has more than `threshold` missing values. 
                If a float, the row will be deleted if it has more than `threshold` proportion of missing values. 
                Defaults to 0.5.
            column (Optional[Union[str, List[str]]], optional): Specific column(s) to consider for missing values.
                If None, considers all columns. Defaults to None.
        """
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be an integer or a float.")
        
        if isinstance(threshold, float) and not (0 <= threshold <= 1):
            raise ValueError("If threshold is a float, it must be between 0.0 and 1.0.")
        
        if isinstance(threshold, int) and threshold < 0:
            raise ValueError("If threshold is an integer, it must be non-negative.")
        
        self.threshold = threshold
        self.column = column
        self.total_columns = None
        self.columns_to_check = None

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

    def fit(self, df) -> 'ListWiseDeleterSpark':
        """
        Fit the listwise deleter to the DataFrame.

        Args:
            df: The PySpark DataFrame to fit the handler to.

        Returns:
            ListWiseDeleterSpark: Self for method chaining.
        """
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")

        # Determine which columns to check for missing values
        if self.column is None:
            self.columns_to_check = df.columns
        else:
            if isinstance(self.column, str):
                self.columns_to_check = [self.column]
            else:
                self.columns_to_check = self.column
            
            # Validate that columns exist in DataFrame
            missing_cols = [col for col in self.columns_to_check if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Columns {missing_cols} not found in DataFrame")

        self.total_columns = len(self.columns_to_check)
        return self
    
    def transform(self, df):
        """
        Transform the DataFrame by removing rows based on the missing value threshold.

        Args:
            df: The PySpark DataFrame to transform.

        Returns:
            DataFrame: The transformed PySpark DataFrame with rows removed.
        """
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")
            
        if self.columns_to_check is None:
            raise ValueError("No columns to check. Please fit the handler first.")
        
        # Create expressions to count missing values for each row in specified columns only
        missing_count_exprs = []
        for column in self.columns_to_check:
            missing_condition = self._get_missing_condition(df, column)
            missing_count_exprs.append(when(missing_condition, 1).otherwise(0))
        
        # Sum up missing values for each row
        df_with_missing_count = df.withColumn(
            "missing_count", 
            sum([expr for expr in missing_count_exprs])
        )
        
        # Apply threshold filtering
        if isinstance(self.threshold, int):
            # Keep rows with missing count less than threshold
            filtered_df = df_with_missing_count.filter(col("missing_count") < self.threshold)
        elif isinstance(self.threshold, float):
            # Keep rows with missing proportion less than threshold
            missing_proportion = col("missing_count") / lit(self.total_columns)
            filtered_df = df_with_missing_count.filter(missing_proportion < self.threshold)
        
        # Remove the helper column and return
        return filtered_df.drop("missing_count")
