import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from statsmodels.discrete.discrete_model import L1BinaryResultsWrapper
from nullsweep.patterns.mar.logistic_regression import MARLogisticRegression

# Test Initialization
def test_initialization_defaults():
    df = pd.DataFrame()
    mar_lr = MARLogisticRegression(df, 'feature')
    
    assert mar_lr.df is df
    assert mar_lr.feature == 'feature'
    assert mar_lr.p_value_threshold == 0.05
    assert mar_lr.pseudo_r_squared_threshold == 0.2

def test_initialization_custom_values():
    df = pd.DataFrame()
    mar_lr = MARLogisticRegression(df, 'feature', p_value_threshold=0.01, pseudo_r_squared_threshold=0.1)
    
    assert mar_lr.df is df
    assert mar_lr.feature == 'feature'
    assert mar_lr.p_value_threshold == 0.01
    assert mar_lr.pseudo_r_squared_threshold == 0.1

# Test detect_pattern Method
def test_detect_pattern_all_numeric_features():
    data = {
        'feature': [1, None, 3, None, 5],
        'candidate1': [10, 20, 30, 40, 50],
        'candidate2': [1, 0, 1, 0, 1]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    with patch.object(mar_lr, '_check_candidate', side_effect=lambda missing, candidate: mar_lr._mappings.update({candidate: False})):
        mar, mappings = mar_lr.detect_pattern()

    assert mar is False
    assert mappings == {'candidate1': False, 'candidate2': False}

def test_detect_pattern_with_non_numeric_features():
    data = {
        'feature': [1, None, 3, None, 5],
        'candidate1': [10, 20, 30, 40, 50],
        'candidate2': ['a', 'b', 'c', 'd', 'e']
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    with patch.object(mar_lr, '_check_candidate', side_effect=lambda missing, candidate: mar_lr._mappings.update({candidate: False})):
        mar, mappings = mar_lr.detect_pattern()

    assert mar is False
    assert mappings == {'candidate1': False}

def test_detect_pattern_no_missing_values():
    data = {
        'feature': [1, 2, 3, 4, 5],
        'candidate1': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    mar, mappings = mar_lr.detect_pattern()

    assert mar is False
    assert mappings == {"candidate1": False}

def test_detect_pattern_all_missing_values():
    data = {
        'feature': [None, None, None, None, None],
        'candidate1': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    mar, mappings = mar_lr.detect_pattern()

    assert mar is False
    assert mappings == {"candidate1": False}

def test_detect_pattern_some_missing_values():
    data = {
        'feature': [1, None, 3, None, 5],
        'candidate1': [10, None, 30, None, 50]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    with patch.object(mar_lr, '_check_candidate', side_effect=lambda missing, candidate: mar_lr._mappings.update({candidate: False})):
        mar, mappings = mar_lr.detect_pattern()

    assert mar is False
    assert mappings == {"candidate1": False}

# Test _check_candidate Method
def test_check_candidate_numeric_feature():
    data = {
        'feature': [1, None, 3, None, 5],
        'candidate': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    missing_encoded_values = df['feature'].isna().astype(int)

    with patch.object(mar_lr, '_evaluate_mar', return_value=False):
        mar_lr._check_candidate(missing_encoded_values, 'candidate')

    assert 'candidate' in mar_lr._mappings
    assert mar_lr._mappings['candidate'] is False


def test_check_candidate_non_numeric_feature():
    data = {
        'feature': [1, None, 3, None, 5],
        'candidate': ['a', 'b', 'c', 'd', 'e']
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    missing_encoded_values = df['feature'].isna().astype(int)

    with pytest.raises(ValueError):
        mar_lr._check_candidate(missing_encoded_values, 'candidate')


def test_check_candidate_all_missing():
    data = {
        'feature': [1, None, 3, None, 5],
        'candidate': [None, None, None, None, None]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    missing_encoded_values = df['feature'].isna().astype(int)

    with pytest.raises(ValueError, match="contains no valid numeric values"):
        mar_lr._check_candidate(missing_encoded_values, 'candidate')


def test_check_candidate_no_missing():
    data = {
        'feature': [1, 2, 3, 4, 5],
        'candidate': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    missing_encoded_values = df['feature'].isna().astype(int)

    with patch.object(mar_lr, '_evaluate_mar', return_value=False):
        mar_lr._check_candidate(missing_encoded_values, 'candidate')

    assert 'candidate' in mar_lr._mappings
    assert mar_lr._mappings['candidate'] is False


def test_fit_logistic_success():
    data = {
        'feature': [1, None, 3, None, 5],
        'candidate': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    missing_encoded_values = df['feature'].isna().astype(int)
    cleaned_target_values, df_candidate = mar_lr._clean_data(missing_encoded_values, 'candidate')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    with patch('statsmodels.api.Logit.fit_regularized', return_value=mock_result):
        result = mar_lr._fit_logistic(cleaned_target_values, df_candidate)
    
    assert result is mock_result

def test_fit_logistic_failure():
    data = {
        'feature': [1, None, 3, None, 5],
        'candidate': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    mar_lr = MARLogisticRegression(df, 'feature')

    missing_encoded_values = df['feature'].isna().astype(int)
    cleaned_target_values, df_candidate = mar_lr._clean_data(missing_encoded_values, 'candidate')

    with patch('statsmodels.api.Logit.fit_regularized', side_effect=Exception("Logit error")):
        with pytest.raises(ValueError, match="Logistic regression model fitting failed. Ensure the data is appropriate for logistic regression. Error details: Logit error"):
            mar_lr._fit_logistic(cleaned_target_values, df_candidate)

def test_evaluate_mar_true():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    mar_lr = MARLogisticRegression(df, 'feature')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    mock_result.pvalues = {'candidate': 0.01}
    mock_result.prsquared = 0.3
    mock_result.llr_pvalue = 0.01

    assert mar_lr._evaluate_mar(mock_result, 'candidate') is True

def test_evaluate_mar_false():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    mar_lr = MARLogisticRegression(df, 'feature')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    mock_result.pvalues = {'candidate': 0.1}
    mock_result.prsquared = 0.1
    mock_result.llr_pvalue = 0.1

    assert mar_lr._evaluate_mar(mock_result, 'candidate') is False

def test_predictor_significant():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    mar_lr = MARLogisticRegression(df, 'feature')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    mock_result.pvalues = {'candidate': 0.01}

    assert mar_lr._is_predictor_significant(mock_result, 'candidate') is True

def test_predictor_not_significant():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    mar_lr = MARLogisticRegression(df, 'feature')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    mock_result.pvalues = {'candidate': 0.1}

    assert mar_lr._is_predictor_significant(mock_result, 'candidate') is False


def test_model_fit_significant():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    mar_lr = MARLogisticRegression(df, 'feature')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    mock_result.prsquared = 0.3

    assert mar_lr._is_model_fit_significant(mock_result) is True

def test_model_fit_not_significant():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    mar_lr = MARLogisticRegression(df, 'feature')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    mock_result.prsquared = 0.1

    assert mar_lr._is_model_fit_significant(mock_result) is False

def test_lrt_significant():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    mar_lr = MARLogisticRegression(df, 'feature')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    mock_result.llr_pvalue = 0.01

    assert mar_lr._is_lrt_significant(mock_result) is True

def test_lrt_not_significant():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    mar_lr = MARLogisticRegression(df, 'feature')

    mock_result = MagicMock(spec=L1BinaryResultsWrapper)
    mock_result.llr_pvalue = 0.1

    assert mar_lr._is_lrt_significant(mock_result) is False