import pytest
import pandas as pd
import numpy as np
from scipy.stats import shapiro
from unittest.mock import patch, MagicMock
from nullsweep.impute.single.decision import SingleImputationStrategyDecider
from nullsweep.utils.structs import Structs

def test_decide_imputation_strategy_continuous_mean():
    decider = SingleImputationStrategyDecider()
    series = pd.Series([1.1, 1.2, 1.3, 1.4, 1.5])

    # Mock the skew and shapiro functions
    with patch('scipy.stats.skew', return_value=0.1), \
         patch('scipy.stats.shapiro') as mock_shapiro, \
         patch.object(SingleImputationStrategyDecider, '_is_time_series', return_value=False), \
         patch.object(SingleImputationStrategyDecider, '_has_sporadic_missing_values', return_value=False):
        
        # Create a mock return value for shapiro with a pvalue attribute
        mock_shapiro_result = MagicMock()
        mock_shapiro_result.pvalue = 0.1  # Assume non-significant skewness
        mock_shapiro.return_value = mock_shapiro_result
    
        strategy = decider.decide_imputation_strategy(series)
        assert strategy == "mean"

def test_decide_imputation_strategy_continuous_median():
    decider = SingleImputationStrategyDecider()
    series = pd.Series([1, 2, 3, 4, 100])

    # Mock the skew and shapiro functions
    with patch('scipy.stats.skew', return_value=2.0), \
         patch('scipy.stats.shapiro') as mock_shapiro, \
         patch.object(SingleImputationStrategyDecider, '_is_time_series', return_value=False), \
         patch.object(SingleImputationStrategyDecider, '_has_sporadic_missing_values', return_value=False):

        mock_shapiro_result = MagicMock()
        mock_shapiro_result.pvalue = 0.01  # Significant skewness
        mock_shapiro.return_value = mock_shapiro_result

        strategy = decider.decide_imputation_strategy(series)
        assert strategy == "median"

def test_decide_imputation_strategy_categorical():
    decider = SingleImputationStrategyDecider()
    series = pd.Series(['a', 'b', 'a', None, 'b'])

    with patch.object(Structs, 'detect_series_type', return_value='categorical'):
        strategy = decider.decide_imputation_strategy(series)
        assert strategy == "most_frequent"


def test_decide_imputation_strategy_date():
    decider = SingleImputationStrategyDecider()
    dates = pd.date_range("2023-01-01", periods=5, freq='D')
    series = pd.Series([1, None, 3, None, 5], index=dates)

    with patch.object(Structs, 'detect_series_type', return_value='date'):
        strategy = decider.decide_imputation_strategy(series)
        assert strategy == "interpolate"


def test_decide_imputation_strategy_continuous_interpolate():
    decider = SingleImputationStrategyDecider()
    dates = pd.date_range("2023-01-01", periods=5, freq='D')
    series = pd.Series([1, None, 3, None, 5], index=dates)

    with patch.object(Structs, 'detect_series_type', return_value='continuous'), \
         patch.object(SingleImputationStrategyDecider, '_is_time_series', return_value=True), \
         patch.object(SingleImputationStrategyDecider, '_has_sporadic_missing_values', return_value=True):

        strategy = decider.decide_imputation_strategy(series)
        assert strategy == "interpolate"

def test_is_time_series_with_datetime_index():
    decider = SingleImputationStrategyDecider()
    dates = pd.date_range("2023-01-01", periods=5, freq='D')
    series = pd.Series([1, 2, 3, 4, 5], index=dates)

    assert decider._is_time_series(series) is True

def test_is_time_series_with_non_datetime_index():
    decider = SingleImputationStrategyDecider()
    series = pd.Series([1, 2, 3, 4, 5], index=[5, 3, 2, 4, 1])  # Non-monotonic, non-datetime index

    assert decider._is_time_series(series) is False

def test_has_sporadic_missing_values_true():
    decider = SingleImputationStrategyDecider()
    series = pd.Series([1, 2, None, 4, 5, 6, 7, 8, 9, 10])

    result = decider._has_sporadic_missing_values(series)
    assert result == True 

def test_has_sporadic_missing_values_false():
    decider = SingleImputationStrategyDecider()
    series = pd.Series([None, None, None, None, 5])

    result = decider._has_sporadic_missing_values(series)
    assert not result

def test_decide_imputation_strategy_invalid_type():
    decider = SingleImputationStrategyDecider()
    series = pd.Series([None, None, None, None])

    with patch.object(Structs, 'detect_series_type', return_value='invalid_type'):
        strategy = decider.decide_imputation_strategy(series)
        assert strategy is None

def test_custom_thresholds():
    thresholds = {
        "skewness": 1.0,
        "shapiro_p_value": 0.1,
        "sporadic": 0.3
    }
    decider = SingleImputationStrategyDecider(thresholds=thresholds)
    assert decider._thresholds == thresholds
