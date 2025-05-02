import pandas as pd
import polars as pl
import dask.dataframe as dd
from typing import Union

DataType = Union[pd.DataFrame, pl.DataFrame, dd.DataFrame]