from pyspark.sql import DataFrame as SparkDataFrame, Window
from pyspark.sql.functions import col, when, isnan, lit, last, first, row_number
from ....bases.handler import AHandler


class DirectionFillImputerSpark(AHandler):
    """
    Spark implementation for direction-based imputation (forward fill and backward fill).
    """
    
    def __init__(self, strategy: str, column: str, **kwargs):
        """
        Args:
            strategy: Imputation strategy ('forwardfill' or 'backfill')
            column: Column name to impute
        """
        if strategy not in ['forwardfill', 'backfill']:
            raise ValueError(f"Strategy '{strategy}' not supported. Use 'forwardfill' or 'backfill'.")
        
        self.strategy = strategy
        self.column = column
        
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

    def fit(self, df: SparkDataFrame) -> "DirectionFillImputerSpark":
        """Direction fill doesn't require fitting"""
        return self

    def transform(self, df: SparkDataFrame) -> SparkDataFrame:
        """Apply direction-based imputation"""
        
        # Add row numbers to maintain order
        window_spec = Window.orderBy(lit(1))  # Order by a constant to maintain original order
        df_with_row_num = df.withColumn("row_num", row_number().over(window_spec))
        
        missing_condition = self._get_missing_condition(df_with_row_num, self.column)
        
        if self.strategy == "forwardfill":
            # Forward fill: use last non-null value
            window_fill = Window.orderBy("row_num").rowsBetween(Window.unboundedPreceding, 0)
            result_df = df_with_row_num.withColumn(
                self.column,
                when(missing_condition, 
                     last(col(self.column), True).over(window_fill))
                .otherwise(col(self.column))
            )
        
        elif self.strategy == "backfill":
            # Backward fill: use first non-null value looking forward
            window_fill = Window.orderBy("row_num").rowsBetween(0, Window.unboundedFollowing)
            result_df = df_with_row_num.withColumn(
                self.column,
                when(missing_condition, 
                     first(col(self.column), True).over(window_fill))
                .otherwise(col(self.column))
            )
        
        # Remove the temporary row number column
        return result_df.drop("row_num")
