import pytest
import pandas as pd
import numpy as np
from nullsweep.impute.single.interpolate import LinearInterpolationImputer


def test_linear_interpolation_imputer_initialization():
    imputer = LinearInterpolationImputer(method="linear")
    assert imputer.method == "linear"
    assert imputer.is_fitted is False

def test_linear_interpolation_imputer_fit():
    imputer = LinearInterpolationImputer()
    series = pd.Series([1, 2, None, 4])

    result = imputer.fit(series)
    assert result is imputer  # Ensure fit returns self
    assert imputer.is_fitted is True  # Ensure is_fitted is set to True


def test_linear_interpolation_imputer_fit_empty_series():
    imputer = LinearInterpolationImputer()
    series = pd.Series([])

    with pytest.raises(ValueError, match="Cannot fit an imputer on an empty Series"):
        imputer.fit(series)

def test_linear_interpolation_imputer_transform_not_fitted():
    imputer = LinearInterpolationImputer()
    series = pd.Series([1, None, 2])

    with pytest.raises(RuntimeError, match="This LinearInterpolationImputer instance is not fitted yet."):
        imputer.transform(series)


def test_linear_interpolation_imputer_transform():
    imputer = LinearInterpolationImputer(method="linear")
    series = pd.Series([1, None, 3, None, 5])

    imputer.fit(series)
    transformed = imputer.transform(series)
    expected = pd.Series([1, 2, 3, 4, 5], dtype=float)  # Match dtype to float64
    
    pd.testing.assert_series_equal(transformed, expected)
