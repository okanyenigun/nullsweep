from pyspark.sql import DataFrame as SparkDataFrame, Window
from pyspark.sql.functions import col, when, isnan, lit, row_number, lag, lead
from ....bases.handler import AHandler


class LinearInterpolationImputerSpark(AHandler):
    """
    Spark implementation for linear interpolation imputation.
    Note: This is a simplified implementation that works for basic cases.
    For complex interpolation, consider using the pandas decorator approach.
    """
    
    def __init__(self, column: str, method: str = "linear", **kwargs):
        """
        Args:
            column: Column name to impute
            method: Interpolation method (only 'linear' supported)
        """
        if method != "linear":
            raise ValueError(f"Only 'linear' interpolation is supported in Spark implementation, got '{method}'")
        
        self.column = column
        self.method = method
        
    def _get_missing_condition(self, df: SparkDataFrame, column_name: str):
        """Get condition for missing values (handles both null and 'NaN' string)"""
        col_obj = col(column_name)
        
        # Get column data type
        col_type = dict(df.dtypes)[column_name]
        
        if col_type in ['double', 'float', 'int', 'bigint', 'smallint', 'tinyint']:
            # For numeric columns, check both isNull and isnan
            return col_obj.isNull() | isnan(col_obj)
        else:
            # For string columns, check isNull and string representations
            return (col_obj.isNull() | 
                   (col_obj == "NaN") | 
                   (col_obj == "nan") | 
                   (col_obj == "null") |
                   (col_obj == ""))

    def fit(self, df: SparkDataFrame) -> "LinearInterpolationImputerSpark":
        """Linear interpolation doesn't require fitting"""
        # Validate that column is numeric
        col_type = dict(df.dtypes)[self.column]
        if col_type not in ['double', 'float', 'int', 'bigint', 'smallint', 'tinyint']:
            raise ValueError(f"Linear interpolation requires numeric column, but '{self.column}' is of type '{col_type}'")
        return self

    def transform(self, df: SparkDataFrame) -> SparkDataFrame:
        """Apply linear interpolation"""
        
        # Add row numbers to maintain order for interpolation
        window_spec = Window.orderBy(lit(1))  # Order by a constant to maintain original order
        df_with_row_num = df.withColumn("row_num", row_number().over(window_spec))
        
        # Define window for getting previous and next values
        window_prev_next = Window.orderBy("row_num")
        
        missing_condition = self._get_missing_condition(df_with_row_num, self.column)
        
        # Get previous and next non-null values
        df_with_neighbors = df_with_row_num.withColumn(
            "prev_value", 
            lag(when(~missing_condition, col(self.column)), 1).over(window_prev_next)
        ).withColumn(
            "next_value",
            lead(when(~missing_condition, col(self.column)), 1).over(window_prev_next)
        )
        
        # Simple linear interpolation: use average of previous and next values
        # For more sophisticated interpolation, would need to consider distances
        result_df = df_with_neighbors.withColumn(
            self.column,
            when(missing_condition & col("prev_value").isNotNull() & col("next_value").isNotNull(),
                 (col("prev_value") + col("next_value")) / 2)
            .when(missing_condition & col("prev_value").isNotNull() & col("next_value").isNull(),
                  col("prev_value"))  # Forward fill if no next value
            .when(missing_condition & col("prev_value").isNull() & col("next_value").isNotNull(),
                  col("next_value"))  # Backward fill if no previous value
            .otherwise(col(self.column))
        )
        
        # Remove temporary columns
        return result_df.drop("row_num", "prev_value", "next_value")
