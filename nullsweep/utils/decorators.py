import functools
import polars as pl
import pandas as pd


def to_pandas(func):
    """
    Decorator to convert Polars DataFrames in function arguments to Pandas DataFrames,
    and convert the function's outputs back to Polars DataFrames if the inputs were Polars.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Track whether any input was a Polars DataFrame
        convert_back = False

        # Convert Polars DataFrames in args to Pandas DataFrames
        new_args = []
        for arg in args:
            if isinstance(arg, pl.DataFrame):
                new_args.append(arg.to_pandas())
                convert_back = True  # Mark that we need to convert outputs back
            else:
                new_args.append(arg)
        
        # Convert Polars DataFrames in kwargs to Pandas DataFrames
        new_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, pl.DataFrame):
                new_kwargs[key] = value.to_pandas()
                convert_back = True  # Mark that we need to convert outputs back
            else:
                new_kwargs[key] = value
        
        # Call the original function with the converted arguments
        result = func(*new_args, **new_kwargs)
        
        # Convert the result back to Polars DataFrame if necessary
        if convert_back:
            if isinstance(result, pd.DataFrame):
                result = pl.DataFrame(result)
            elif isinstance(result, (list, tuple)):
                # Handle multiple outputs (e.g., tuples or lists)
                result = type(result)(
                    pl.DataFrame(item) if isinstance(item, pd.DataFrame) else item
                    for item in result
                )
        
        return result
    
    return wrapper

def series_to_pandas(func):
    """
    Decorator to convert Polars Series in function arguments to Pandas Series,
    and convert the function's outputs back to Polars Series if the inputs were Polars.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Track whether any input was a Polars Series
        convert_back = False

        # Convert Polars Series in args to Pandas Series
        new_args = []
        for arg in args:
            if isinstance(arg, pl.Series):
                new_args.append(arg.to_pandas())
                convert_back = True  # Mark that we need to convert outputs back
            else:
                new_args.append(arg)
        
        # Convert Polars Series in kwargs to Pandas Series
        new_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, pl.Series):
                new_kwargs[key] = value.to_pandas()
                convert_back = True  # Mark that we need to convert outputs back
            else:
                new_kwargs[key] = value
        
        # Call the original function with the converted arguments
        result = func(*new_args, **new_kwargs)
        
        # Convert the result back to Polars Series if necessary
        if convert_back:
            if isinstance(result, pd.Series):
                result = pl.Series(result)
            elif isinstance(result, (list, tuple)):
                # Handle multiple outputs (e.g., tuples or lists)
                result = type(result)(
                    pl.Series(item) if isinstance(item, pd.Series) else item
                    for item in result
                )
        
        return result
    
    return wrapper