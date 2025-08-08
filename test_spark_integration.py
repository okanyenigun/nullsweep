#!/usr/bin/env python3
"""
Test script to verify PySpark integration with nullsweep
"""

import pandas as pd
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col
    SPARK_AVAILABLE = True
except ImportError:
    print("PySpark is not available. Please install it first.")
    SPARK_AVAILABLE = False

if SPARK_AVAILABLE:
    # Create SparkSession
    spark = SparkSession.builder \
        .appName("NullSweepTest") \
        .config("spark.sql.adaptive.enabled", "false") \
        .getOrCreate()

    # Create test data with missing values
    pandas_df = pd.DataFrame({
        'A': [1, 2, None, 4, 5],
        'B': [1, None, None, None, 5],
        'C': [1, 2, 3, 4, 5]
    })

    # Convert to Spark DataFrame
    spark_df = spark.createDataFrame(pandas_df)

    print("Original DataFrame:")
    spark_df.show()

    # Test our new Spark engine
    from nullsweep.patterns.monotone.spark_engine import SparkDFPatternDetector

    detector = SparkDFPatternDetector(spark_df)

    print("\nTesting univariate detection...")
    univariate_result = detector.detect_univariate()
    print(f"Univariate result: {univariate_result}")

    print("\nTesting monotone detection...")
    monotone_result, monotone_matrix = detector.detect_monotone()
    print(f"Monotone pattern detected: {monotone_result}")
    if monotone_result:
        print("Monotone matrix:")
        print(monotone_matrix)

    print("\nTesting full pattern detection...")
    pattern, data = detector.detect_pattern()
    print(f"Pattern: {pattern}")
    print(f"Data: {data}")

    # Test with DatasetPatternManager
    print("\nTesting with DatasetPatternManager...")
    from nullsweep.patterns.df import DatasetPatternManager

    manager = DatasetPatternManager()
    pattern, data = manager.detect_pattern("coarse", spark_df)
    print(f"Manager Pattern: {pattern}")
    print(f"Manager Data: {data}")

    spark.stop()
else:
    print("Skipping test - PySpark not available")
