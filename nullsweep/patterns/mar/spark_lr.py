import pandas as pd
from typing import Dict, Tuple
from .base import MarTypeLogisticDetector

try:
    from pyspark.sql.functions import col, isnan, when
    SPARK_AVAILABLE = True
except ImportError:
    SparkDataFrame = None
    SPARK_AVAILABLE = False



class MarLRSpark(MarTypeLogisticDetector):
    """
    PySpark implementation of MAR logistic regression detector.
    """

    def _is_numeric_column(self, column_name: str) -> bool:
        """Check if a column is numeric type."""
        column_type = dict(self.df.dtypes)[column_name]
        numeric_types = ['int', 'bigint', 'float', 'double', 'decimal']
        return any(numeric_type in column_type.lower() for numeric_type in numeric_types)

    def _get_missing_condition(self, column_name: str):
        """Get the appropriate missing value condition based on column type."""
        if self._is_numeric_column(column_name):
            return col(column_name).isNull() | isnan(col(column_name))
        else:
            # For string columns, also check for common string representations of missing values
            return (col(column_name).isNull() | 
                   (col(column_name) == "") | 
                   (col(column_name) == "NaN") | 
                   (col(column_name) == "nan") |
                   (col(column_name) == "null") |
                   (col(column_name) == "NULL"))

    def detect_pattern(self) -> Tuple[bool, Dict[str, bool]]:
        if not SPARK_AVAILABLE:
            raise ImportError(
                "PySpark is not available. Please install pyspark to use Spark engine.")

        # Create missing encoded values (1 for missing, 0 for not missing)
        missing_condition = self._get_missing_condition(self.feature)
        df_with_missing = self.df.withColumn(
            "missing_encoded", 
            when(missing_condition, 1).otherwise(0)
        )

        candidate_feature_list = [col_name for col_name in self.df.columns if col_name != self.feature]

        for candidate in candidate_feature_list:
            # Only process numeric columns
            if not self._is_numeric_column(candidate):
                continue

            self._check_candidate(df_with_missing, candidate)
        
        return self._mar, self._mappings
    
    def _check_candidate(self, df_with_missing, candidate: str) -> None:
        """
        Checks if the candidate feature indicates an MAR pattern.
        
        Args:
            df_with_missing: DataFrame with missing values encoded.
            candidate (str): The candidate feature to check.
        """
        cleaned_target_values, df_candidate = self._clean_data(df_with_missing, candidate)

        if cleaned_target_values.empty or df_candidate.empty:
            self._mappings[candidate] = False
            return
        
        try:
            model_result = self._fit_logistic(cleaned_target_values, df_candidate)
            self._mappings[candidate] = self._evaluate_mar(model_result, candidate)
            
            if self._mappings[candidate]:
                self._mar = True
        except Exception as e:
            # If model fitting fails, assume no MAR pattern
            self._mappings[candidate] = False
        
        return
    
    def _clean_data(self, df_with_missing, candidate: str) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Cleans the data by removing rows with missing values in the candidate feature.
        
        Args:
            df_with_missing: DataFrame with missing values encoded.
            candidate (str): The candidate feature to clean.
        
        Returns:
            Tuple[pd.Series, pd.DataFrame]: The cleaned target values and candidate DataFrame.
        """
        # Filter out rows where the candidate column has missing values
        candidate_missing_condition = self._get_missing_condition(candidate)
        cleaned_df = df_with_missing.filter(~candidate_missing_condition)

        # Check if we have any data left after cleaning
        if cleaned_df.count() == 0:
            return pd.Series(), pd.DataFrame()

        # Convert to pandas for statsmodels compatibility
        pandas_df = cleaned_df.select("missing_encoded", candidate).toPandas()
        
        if pandas_df.empty:
            return pd.Series(), pd.DataFrame()
        
        cleaned_target_values = pandas_df["missing_encoded"]
        cleaned_candidate_values = pandas_df[candidate]

        # Reset index and prepare DataFrame for logistic regression
        cleaned_target_values.reset_index(drop=True, inplace=True)
        cleaned_candidate_values.reset_index(drop=True, inplace=True)
        
        # Create DataFrame with candidate feature and intercept column
        df_candidate = cleaned_candidate_values.to_frame()
        df_candidate['new_column'] = 1  # Intercept term
        
        return cleaned_target_values, df_candidate
