import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from unittest.mock import MagicMock
from nullsweep.patterns.mtype.mar_based import MarBasedDetection
from nullsweep.patterns.mtype.mar_based import MARLogisticRegression
from nullsweep.utils.dummies import Dummy

@pytest.fixture
def dataframes():
    # Define various dataframes for testing
    df_missing_mar = Dummy.get_mar_df()
    df_missing_mcar = pd.DataFrame({
        'A': [None, 2, 3, None],
        'B': [1, None, None, 4]
    })
    df_no_missing = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': [5, 6, 7, 8]
    })
    df_empty = pd.DataFrame()

    return {
        'df_missing_mar': df_missing_mar,
        'df_missing_mcar': df_missing_mcar,
        'df_no_missing': df_no_missing,
        'df_empty': df_empty
    }

@pytest.fixture
def mock_logistic_regression():
    with patch('nullsweep.patterns.mtype.mar_based.MARLogisticRegression', autospec=True) as MockLogisticRegression:
        instance = MockLogisticRegression.return_value
        instance.detect_pattern = MagicMock(return_value=(True, {"info": "MAR pattern detected"}))
        yield MockLogisticRegression

def test_decide_logistic_mar_pattern(dataframes, mock_logistic_regression):
    mock_logistic_regression.return_value.detect_pattern.return_value = (True, {"info": "MAR pattern detected"})
    detector = MarBasedDetection()
    pattern, data = detector.decide("logistic", dataframes['df_missing_mar'], 'A')
    assert pattern == "MAR"
    assert data == {"info": "MAR pattern detected"}

def test_decide_logistic_mcar_pattern(dataframes, mock_logistic_regression):
    mock_logistic_regression.return_value.detect_pattern.return_value = (False, {"info": "MCAR pattern detected"})
    detector = MarBasedDetection()
    pattern, data = detector.decide("logistic", dataframes['df_missing_mcar'], 'A')
    assert pattern == "MCAR"
    assert data == {"info": "MCAR pattern detected"}

def test_decide_unsupported_method(dataframes):
    detector = MarBasedDetection()
    with pytest.raises(ValueError, match="Unsupported method 'unsupported'. Supported methods are: \['logistic'\]"):
        detector.decide("unsupported", dataframes['df_missing_mar'], 'A')

def test_decide_no_missing_data(dataframes, mock_logistic_regression):
    mock_logistic_regression.return_value.detect_pattern.return_value = (False, {"info": "No missing data"})
    detector = MarBasedDetection()
    pattern, data = detector.decide("logistic", dataframes['df_no_missing'], 'A')
    assert pattern == "MCAR"
    assert data == {"info": "No missing data"}

def test_decide_empty_dataframe(dataframes, mock_logistic_regression):
    mock_logistic_regression.return_value.detect_pattern.return_value = (False, {"info": "Empty DataFrame"})
    detector = MarBasedDetection()
    pattern, data = detector.decide("logistic", dataframes['df_empty'], 'A')
    assert pattern == "MCAR"
    assert data == {"info": "Empty DataFrame"}