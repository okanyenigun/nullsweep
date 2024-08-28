import pytest
import pandas as pd
import numpy as np
from nullsweep.impute.single.direction import DirectionFillImputer

def test_direction_fill_imputer_initialization():
    # Test valid initialization
    imputer = DirectionFillImputer(strategy='forwardfill')
    assert imputer.strategy == 'forwardfill'
    assert imputer.is_fitted is False

    imputer = DirectionFillImputer(strategy='backfill')
    assert imputer.strategy == 'backfill'
    assert imputer.is_fitted is False

    # Test invalid strategy
    with pytest.raises(ValueError, match="Strategy must be either 'forwardfill' or 'backfill'."):
        DirectionFillImputer(strategy='invalid_strategy')

def test_direction_fill_imputer_fit():
    imputer = DirectionFillImputer(strategy='forwardfill')
    series = pd.Series([1, 2, None, 4])

    result = imputer.fit(series)
    assert result is imputer  # Ensure fit returns self
    assert imputer.is_fitted is True  # Ensure is_fitted is set to True


def test_direction_fill_imputer_transform_forwardfill():
    imputer = DirectionFillImputer(strategy='forwardfill')
    series = pd.Series([1, None, 2, None, 3])

    imputer.fit(series)
    transformed = imputer.transform(series)
    expected = pd.Series([1, 1, 2, 2, 3], dtype=float)  # Explicitly set dtype to float
    
    pd.testing.assert_series_equal(transformed, expected)

def test_direction_fill_imputer_transform_backfill():
    imputer = DirectionFillImputer(strategy='backfill')
    series = pd.Series([1, None, 2, None, 3])

    imputer.fit(series)
    transformed = imputer.transform(series)
    expected = pd.Series([1, 2, 2, 3, 3], dtype=float)  # Match dtype
    
    pd.testing.assert_series_equal(transformed, expected)

def test_direction_fill_imputer_transform_not_fitted():
    imputer = DirectionFillImputer(strategy='forwardfill')
    series = pd.Series([1, None, 2])

    with pytest.raises(RuntimeError, match="This FillImputer instance is not fitted yet."):
        imputer.transform(series)


def test_direction_fill_imputer_transform_with_numpy_array():
    imputer = DirectionFillImputer(strategy='forwardfill')
    array = np.array([1, None, 2, None, 3], dtype=object)

    imputer.fit(array)
    transformed = imputer.transform(array)
    expected = pd.Series([1, 1, 2, 2, 3], dtype=int)  # Match dtype to int
    
    pd.testing.assert_series_equal(transformed, expected)


def test_direction_fill_imputer_fit_transform():
    imputer = DirectionFillImputer(strategy='forwardfill')
    series = pd.Series([1, None, 2, None, 3])

    transformed = imputer.fit_transform(series)
    expected = pd.Series([1, 1, 2, 2, 3], dtype=float)  # Match dtype
    
    pd.testing.assert_series_equal(transformed, expected)