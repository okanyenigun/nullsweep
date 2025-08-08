from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.functions import col, when, isnan, isnull, mean, expr, lit
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from typing import Optional, Union, Iterable, Any
from .....bases.handler import AHandler


class RegressionImputerSpark(AHandler):
    """
    Spark-native regression imputer using MLlib's LinearRegression.
    """

    def __init__(
        self,
        column: Optional[Union[str, Iterable[str]]] = None,
        estimator: Any = None,
        predictor_strategy: str = "mean"
    ):
        """
        Args:
            column: Target column(s) to impute. If None, all columns with nulls.
            estimator: Not used (Spark uses native LinearRegression)
            predictor_strategy: Strategy for filling predictor nulls ("mean", "median", "most_frequent")
        """
        if predictor_strategy not in {"mean", "median", "most_frequent"}:
            raise ValueError("`predictor_strategy` must be one of 'mean', 'median', or 'most_frequent'.")
            
        self.column = column
        self.predictor_strategy = predictor_strategy
        self.models = {}
        self.feature_columns = {}

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

    def _fill_missing_predictors(self, df: SparkDataFrame, predictors: list) -> SparkDataFrame:
        """Fill missing values in predictor columns based on strategy (only numeric columns)"""
        result_df = df
        
        for pred_col in predictors:
            col_type = dict(df.dtypes)[pred_col]
            
            # Only process numeric columns (should already be filtered, but double-check)
            if col_type not in ['double', 'float', 'int', 'bigint', 'smallint', 'tinyint']:
                continue
            
            # Check if column has any missing values
            missing_condition = self._get_missing_condition(df, pred_col)
            if df.filter(missing_condition).count() == 0:
                continue  # No missing values in this column
                
            if self.predictor_strategy == "mean":
                # Calculate mean for numeric columns, excluding nulls and NaNs
                mean_val = df.filter(~missing_condition).select(mean(col(pred_col))).collect()[0][0]
                if mean_val is not None:
                    result_df = result_df.withColumn(
                        pred_col,
                        when(missing_condition, lit(mean_val))
                        .otherwise(col(pred_col))
                    )
            elif self.predictor_strategy == "median":
                # Calculate median for numeric columns, excluding nulls and NaNs
                median_val = df.filter(~missing_condition).select(expr(f"percentile_approx({pred_col}, 0.5)")).collect()[0][0]
                if median_val is not None:
                    result_df = result_df.withColumn(
                        pred_col,
                        when(missing_condition, lit(median_val))
                        .otherwise(col(pred_col))
                    )
            elif self.predictor_strategy == "most_frequent":
                # Get most frequent value, excluding nulls and NaNs
                mode_row = (df.filter(~missing_condition)
                           .groupBy(pred_col)
                           .count()
                           .orderBy(col("count").desc())
                           .first())
                if mode_row:
                    mode_val = mode_row[pred_col]
                    result_df = result_df.withColumn(
                        pred_col,
                        when(missing_condition, lit(mode_val))
                        .otherwise(col(pred_col))
                    )
        
        return result_df

    def fit(self, df: SparkDataFrame) -> "RegressionImputerSpark":
        """Fit regression models for each target column"""
        
        if self.column is None:
            # Find all columns with missing values
            self.column = []
            for col_name in df.columns:
                null_count = df.filter(self._get_missing_condition(df, col_name)).count()
                if null_count > 0:
                    self.column.append(col_name)
        elif isinstance(self.column, str):
            self.column = [self.column]
        else:
            self.column = list(self.column)

        for target_col in self.column:
            # Get all predictor columns (all except target)
            all_predictors = [c for c in df.columns if c != target_col]
            
            # Filter to only numeric predictors for MLlib regression
            numeric_predictors = []
            for pred_col in all_predictors:
                col_type = dict(df.dtypes)[pred_col]
                if col_type in ['double', 'float', 'int', 'bigint', 'smallint', 'tinyint']:
                    numeric_predictors.append(pred_col)
            
            if len(numeric_predictors) == 0:
                raise ValueError(f"No numeric predictors available for column '{target_col}'. "
                               "Regression imputation requires at least one numeric predictor column.")
            
            # Get training data (rows where target is not null)
            train_df = df.filter(~self._get_missing_condition(df, target_col))
            
            if train_df.count() == 0:
                continue
                
            # Fill missing predictor values
            train_df = self._fill_missing_predictors(train_df, numeric_predictors)
            
            # Ensure no NaN values remain by dropping any rows with null/NaN in numeric predictors
            for pred_col in numeric_predictors:
                train_df = train_df.filter(~self._get_missing_condition(train_df, pred_col))
            
            # Check if we have enough training data
            if train_df.count() == 0:
                raise ValueError(f"No valid training data remaining for column '{target_col}' after removing rows with missing predictors.")
            
            # Prepare features using VectorAssembler (only numeric columns)
            assembler = VectorAssembler(
                inputCols=numeric_predictors,
                outputCol="features",
                handleInvalid="keep"  # Keep rows with NaN/null values, but we should handle them beforehand
            )
            
            train_assembled = assembler.transform(train_df)
            
            # Train linear regression model
            lr = LinearRegression(
                featuresCol="features",
                labelCol=target_col,
                predictionCol="prediction"
            )
            
            model = lr.fit(train_assembled)
            
            # Store model, assembler, and feature columns
            self.models[target_col] = (model, assembler)
            self.feature_columns[target_col] = numeric_predictors

        return self

    def transform(self, df: SparkDataFrame) -> SparkDataFrame:
        """Transform DataFrame by imputing missing values using fitted models"""
        
        if not self.models:
            raise ValueError("The imputer has not been fitted yet. Call 'fit' first.")
        
        result_df = df
        
        for target_col, (model, assembler) in self.models.items():
            # Get rows with missing target values
            missing_condition = self._get_missing_condition(result_df, target_col)
            
            # Count missing values for debugging
            missing_count = result_df.filter(missing_condition).count()
            if missing_count == 0:
                continue
                
            # Fill missing predictor values for the entire DataFrame
            predictors = self.feature_columns[target_col]
            filled_df = self._fill_missing_predictors(result_df, predictors)
            
            # Apply the assembler to create features
            assembled_df = assembler.transform(filled_df)
            
            # Make predictions for all rows
            predictions_df = model.transform(assembled_df)
            
            # Update the target column: use prediction where target was missing, otherwise keep original
            result_df = predictions_df.withColumn(
                target_col,
                when(missing_condition, col("prediction"))
                .otherwise(col(target_col))
            ).drop("features", "prediction")  # Clean up temporary columns

        return result_df
