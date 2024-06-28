import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from nullsweep.patterns.feature import FeaturePatternManager

@pytest.fixture
def dataframes():
    # Define various dataframes for testing
    df_missing_mar = pd.DataFrame({
        'A': [1, None, 3, None],
        'B': [5, 6, None, 8]
    })
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

# Mock the MarBasedDetection class
@pytest.fixture
def mock_mar_based_detection():
    with patch('nullsweep.patterns.feature.MarBasedDetection', autospec=True) as MockMarBasedDetection:
        instance = MockMarBasedDetection.return_value
        instance.decide = MagicMock()
        yield MockMarBasedDetection

# Unit tests for detect_pattern method
def test_detect_pattern_mar_based_logistic_mar_pattern(dataframes, mock_mar_based_detection):
    mock_mar_based_detection.return_value.decide.return_value = ("MAR", {"info": "MAR pattern detected"})
    manager = FeaturePatternManager()
    pattern, data = manager.detect_pattern("mar_based", "logistic", dataframes['df_missing_mar'], 'A')
    assert pattern == "MAR"
    assert data == {"info": "MAR pattern detected"}

def test_detect_pattern_mar_based_logistic_mcar_pattern(dataframes, mock_mar_based_detection):
    mock_mar_based_detection.return_value.decide.return_value = ("MCAR", {"info": "MCAR pattern detected"})
    manager = FeaturePatternManager()
    pattern, data = manager.detect_pattern("mar_based", "logistic", dataframes['df_missing_mcar'], 'A')
    assert pattern == "MCAR"
    assert data == {"info": "MCAR pattern detected"}

def test_detect_pattern_unsupported_approach(dataframes):
    manager = FeaturePatternManager()
    with pytest.raises(ValueError, match="Unsupported approach 'unsupported'. Supported approaches are: \['mar_based'\]"):
        manager.detect_pattern("unsupported", "logistic", dataframes['df_missing_mar'], 'A')

def test_detect_pattern_no_missing_data(dataframes, mock_mar_based_detection):
    mock_mar_based_detection.return_value.decide.return_value = ("MCAR", {"info": "No missing data"})
    manager = FeaturePatternManager()
    pattern, data = manager.detect_pattern("mar_based", "logistic", dataframes['df_no_missing'], 'A')
    assert pattern == "MCAR"
    assert data == {"info": "No missing data"}


def test_detect_pattern_empty_dataframe(dataframes, mock_mar_based_detection):
    mock_mar_based_detection.return_value.decide.return_value = ("MCAR", {"info": "Empty DataFrame"})
    manager = FeaturePatternManager()
    pattern, data = manager.detect_pattern("mar_based", "logistic", dataframes['df_empty'], 'A')
    assert pattern == "MCAR"
    assert data == {"info": "Empty DataFrame"}
