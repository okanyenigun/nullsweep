from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.functions import col, when, lit
from typing import Optional, Any
from ....bases.handler import AHandler


class SingleCategoricalImputerSpark(AHandler):
    """
    Spark implementation for categorical imputation strategies.
    """
    
    def __init__(self, strategy: str, column: str, fill_value: Optional[Any] = None, **kwargs):
        """
        Args:
            strategy: Imputation strategy ('most_frequent', 'least_frequent', 'constant')
            column: Column name to impute
            fill_value: Value to use for constant strategy
        """
        if strategy not in ['most_frequent', 'least_frequent', 'constant']:
            raise ValueError(f"Strategy '{strategy}' not supported for categorical data. Use 'most_frequent', 'least_frequent', or 'constant'.")
        
        self.strategy = strategy
        self.column = column
        self.fill_value = fill_value
        self.computed_value = None
        
    def _get_missing_condition(self, df: SparkDataFrame, column_name: str):
        """Get condition for missing values (handles both null and 'NaN' string)"""
        col_obj = col(column_name)
        
        # For categorical columns, check isNull and string representations
        return (col_obj.isNull() | 
               (col_obj == "NaN") | 
               (col_obj == "nan") | 
               (col_obj == "null") |
               (col_obj == ""))

    def fit(self, df: SparkDataFrame) -> "SingleCategoricalImputerSpark":
        """Compute the fill value based on the strategy"""
        
        if self.strategy == "constant":
            if self.fill_value is None:
                raise ValueError("fill_value must be provided when using 'constant' strategy")
            self.computed_value = self.fill_value
            
        elif self.strategy == "most_frequent":
            # Find most frequent value excluding missing values
            missing_condition = self._get_missing_condition(df, self.column)
            mode_result = (df.filter(~missing_condition)
                          .groupBy(self.column)
                          .count()
                          .orderBy(col("count").desc())
                          .first())
            if mode_result:
                self.computed_value = mode_result[self.column]
            else:
                raise ValueError(f"Cannot compute most frequent value for column '{self.column}' - no valid values found")
                
        elif self.strategy == "least_frequent":
            # Find least frequent value excluding missing values
            missing_condition = self._get_missing_condition(df, self.column)
            mode_result = (df.filter(~missing_condition)
                          .groupBy(self.column)
                          .count()
                          .orderBy(col("count").asc())
                          .first())
            if mode_result:
                self.computed_value = mode_result[self.column]
            else:
                raise ValueError(f"Cannot compute least frequent value for column '{self.column}' - no valid values found")
        
        return self

    def transform(self, df: SparkDataFrame) -> SparkDataFrame:
        """Apply the imputation to the DataFrame"""
        
        if self.computed_value is None:
            raise ValueError("Must call fit() before transform()")
        
        missing_condition = self._get_missing_condition(df, self.column)
        
        return df.withColumn(
            self.column,
            when(missing_condition, lit(self.computed_value))
            .otherwise(col(self.column))
        )
