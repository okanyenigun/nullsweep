import functools
import polars as pl
import pandas as pd

try:
    import dask.dataframe as dd
    from dask.dataframe import DataFrame as DaskDataFrame, Series as DaskSeries
    _HAS_DASK = True
except ImportError:
    _HAS_DASK = False


def to_pandas(func):
    """
    Decorator to convert Polars or Dask DataFrames in function arguments to Pandas DataFrames,
    then convert back to the original type (Polars or Dask) on output.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        orig_type = None
        orig_nparts = None

        # Convert args
        new_args = []
        for arg in args:
            if isinstance(arg, pl.DataFrame):
                new_args.append(arg.to_pandas())
                if orig_type is None:
                    orig_type = 'polars'
            elif _HAS_DASK and isinstance(arg, DaskDataFrame):
                # Compute to pandas, record partitions
                orig_nparts = arg.npartitions
                new_args.append(arg.compute())
                if orig_type is None:
                    orig_type = 'dask'
            else:
                new_args.append(arg)

        # Convert kwargs
        new_kwargs = {}
        for key, val in kwargs.items():
            if isinstance(val, pl.DataFrame):
                new_kwargs[key] = val.to_pandas()
                if orig_type is None:
                    orig_type = 'polars'
            elif _HAS_DASK and isinstance(val, DaskDataFrame):
                orig_nparts = val.npartitions
                new_kwargs[key] = val.compute()
                if orig_type is None:
                    orig_type = 'dask'
            else:
                new_kwargs[key] = val

        # Call original
        result = func(*new_args, **new_kwargs)

        # Convert output back
        if orig_type == 'polars':
            if isinstance(result, pd.DataFrame):
                return pl.DataFrame(result)
            if isinstance(result, pd.Series):
                return pl.Series(result)
            if isinstance(result, (list, tuple)):
                return type(result)(
                    pl.DataFrame(r) if isinstance(r, pd.DataFrame) else 
                    pl.Series(r) if isinstance(r, pd.Series) else r
                    for r in result
                )
        elif orig_type == 'dask' and _HAS_DASK:
            if isinstance(result, pd.DataFrame):
                return dd.from_pandas(result, npartitions=orig_nparts)
            if isinstance(result, pd.Series):
                return dd.from_pandas(result, npartitions=orig_nparts)
            if isinstance(result, (list, tuple)):
                def _convert(r):
                    if isinstance(r, pd.DataFrame):
                        return dd.from_pandas(r, npartitions=orig_nparts)
                    if isinstance(r, pd.Series):
                        return dd.from_pandas(r, npartitions=orig_nparts)
                    return r
                return type(result)(_convert(r) for r in result)

        return result

    return wrapper


def series_to_pandas(func):
    """
    Decorator to convert Polars or Dask Series in arguments to Pandas Series,
    then convert back to the original type on output.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        orig_type = None
        orig_nparts = None

        new_args = []
        for arg in args:
            if isinstance(arg, pl.Series):
                new_args.append(arg.to_pandas())
                if orig_type is None:
                    orig_type = 'polars'
            elif _HAS_DASK and isinstance(arg, DaskSeries):
                orig_nparts = arg.npartitions
                new_args.append(arg.compute())
                if orig_type is None:
                    orig_type = 'dask'
            else:
                new_args.append(arg)

        new_kwargs = {}
        for key, val in kwargs.items():
            if isinstance(val, pl.Series):
                new_kwargs[key] = val.to_pandas()
                if orig_type is None:
                    orig_type = 'polars'
            elif _HAS_DASK and isinstance(val, DaskSeries):
                orig_nparts = val.npartitions
                new_kwargs[key] = val.compute()
                if orig_type is None:
                    orig_type = 'dask'
            else:
                new_kwargs[key] = val

        result = func(*new_args, **new_kwargs)

        if orig_type == 'polars':
            if isinstance(result, pd.Series):
                return pl.Series(result)
            if isinstance(result, pd.DataFrame):
                return pl.DataFrame(result)
            if isinstance(result, (list, tuple)):
                return type(result)(
                    pl.Series(r) if isinstance(r, pd.Series) else 
                    pl.DataFrame(r) if isinstance(r, pd.DataFrame) else r
                    for r in result
                )
        elif orig_type == 'dask' and _HAS_DASK:
            if isinstance(result, pd.Series):
                return dd.from_pandas(result, npartitions=orig_nparts)
            if isinstance(result, pd.DataFrame):
                return dd.from_pandas(result, npartitions=orig_nparts)
            if isinstance(result, (list, tuple)):
                def _convert(r):
                    if isinstance(r, pd.Series):
                        return dd.from_pandas(r, npartitions=orig_nparts)
                    if isinstance(r, pd.DataFrame):
                        return dd.from_pandas(r, npartitions=orig_nparts)
                    return r
                return type(result)(_convert(r) for r in result)

        return result

    return wrapper
