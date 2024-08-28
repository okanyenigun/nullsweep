import pytest
import pandas as pd
import numpy as np
from nullsweep.impute.single.categorical import SingleCategoricalImputer

def test_imputer_initialization_invalid_strategy():
    with pytest.raises(ValueError, match="Strategy must be one of 'most_frequent', 'constant', or 'least_frequent'"):
        SingleCategoricalImputer(strategy="invalid_strategy")

def test_imputer_initialization_default_strategy():
    imputer = SingleCategoricalImputer()
    assert imputer.strategy == "most_frequent"
    assert imputer.fill_value is None

def test_fit_empty_series():
    imputer = SingleCategoricalImputer()
    empty_series = pd.Series([])
    with pytest.raises(ValueError, match="Cannot fit on an empty Series"):
        imputer.fit(empty_series)

def test_fit_most_frequent():
    imputer = SingleCategoricalImputer(strategy="most_frequent")
    series = pd.Series(['a', 'b', 'a', None, 'b', 'a'])
    imputer.fit(series)
    assert imputer.fill_value == 'a'

def test_fit_least_frequent():
    imputer = SingleCategoricalImputer(strategy="least_frequent")
    series = pd.Series(['a', 'b', 'a', None, 'b', 'b'])
    imputer.fit(series)
    assert imputer.fill_value == 'a'

def test_fit_constant_value():
    imputer = SingleCategoricalImputer(strategy="constant", fill_value="missing")
    series = pd.Series(['a', 'b', None, 'b', 'a'])
    imputer.fit(series)
    assert imputer.fill_value == "missing"

def test_transform_without_fit():
    imputer = SingleCategoricalImputer(strategy="most_frequent")
    series = pd.Series([None, 'a', 'b'])
    with pytest.raises(ValueError, match="The imputer has not been fitted. Please call 'fit' before 'transform'."):
        imputer.transform(series)

def test_transform_most_frequent():
    imputer = SingleCategoricalImputer(strategy="most_frequent")
    series = pd.Series(['a', 'b', 'a', None, 'b', 'a'])
    imputer.fit(series)
    transformed = imputer.transform(series)
    expected = pd.Series(['a', 'b', 'a', 'a', 'b', 'a'])
    pd.testing.assert_series_equal(transformed, expected)

def test_transform_least_frequent():
    imputer = SingleCategoricalImputer(strategy="least_frequent")
    series = pd.Series(['a', 'b', 'a', None, 'b', 'b'])
    imputer.fit(series)
    transformed = imputer.transform(series)
    expected = pd.Series(['a', 'b', 'a', 'a', 'b', 'b'])
    pd.testing.assert_series_equal(transformed, expected)

def test_transform_constant_value():
    imputer = SingleCategoricalImputer(strategy="constant", fill_value="missing")
    series = pd.Series(['a', 'b', None, 'b', 'a'])
    imputer.fit(series)
    transformed = imputer.transform(series)
    expected = pd.Series(['a', 'b', 'missing', 'b', 'a'])
    pd.testing.assert_series_equal(transformed, expected)

def test_fit_transform_most_frequent():
    imputer = SingleCategoricalImputer(strategy="most_frequent")
    series = pd.Series(['a', 'b', None, 'b', 'a'])
    transformed = imputer.fit_transform(series)
    expected = pd.Series(['a', 'b', 'a', 'b', 'a'])
    pd.testing.assert_series_equal(transformed, expected)

def test_transform_numpy_array():
    imputer = SingleCategoricalImputer(strategy="most_frequent")
    series = np.array(['a', 'b', None, 'b', 'a'])
    imputer.fit(series)
    transformed = imputer.transform(series)
    expected = pd.Series(['a', 'b', 'a', 'b', 'a'])
    pd.testing.assert_series_equal(transformed, expected)
