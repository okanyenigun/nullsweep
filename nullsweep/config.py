import pandas as pd
import polars as pl
import dask.dataframe as dd
from typing import Union

try:
    from pyspark.sql import DataFrame as SparkDataFrame
    SPARK_AVAILABLE = True
except ImportError:
    SparkDataFrame = None
    SPARK_AVAILABLE = False

if SPARK_AVAILABLE:
    DataType = Union[pd.DataFrame, pl.DataFrame, dd.DataFrame, SparkDataFrame]
else:
    DataType = Union[pd.DataFrame, pl.DataFrame, dd.DataFrame]
