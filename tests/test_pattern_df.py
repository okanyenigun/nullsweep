import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from nullsweep.patterns.df import DatasetPatternManager

@pytest.fixture
def dataframes():
    # Define various dataframes for testing
    df_univariate = pd.DataFrame({
        'A': [1, 2, None, 4],
        'B': [5, 6, 7, 8]
    })
    df_monotone = pd.DataFrame({
        'A': [1, None, None, None],
        'B': [2, 3, None, None],
        'C': [4, 5, 6, None]
    })
    df_non_monotone = pd.DataFrame({
        'A': [None, 2, 3, None],
        'B': [1, None, None, 4],
        'C': [None, None, 3, 4]
    })
    df_no_missing = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': [5, 6, 7, 8]
    })
    df_empty = pd.DataFrame()

    return {
        'df_univariate': df_univariate,
        'df_monotone': df_monotone,
        'df_non_monotone': df_non_monotone,
        'df_no_missing': df_no_missing,
        'df_empty': df_empty
    }

# Mock the DataFramePatternDetector class
@pytest.fixture
def mock_dataframe_pattern_detector():
    with patch('nullsweep.patterns.df.DataFramePatternDetector', autospec=True) as MockPatternDetector:
        instance = MockPatternDetector.return_value
        instance.detect_pattern = MagicMock()
        yield MockPatternDetector

# Unit tests for detect_pattern method
def test_detect_pattern_coarse_approach_univariate(dataframes, mock_dataframe_pattern_detector):
    mock_dataframe_pattern_detector.return_value.detect_pattern.return_value = ("univariate", {"column": "A"})
    manager = DatasetPatternManager()
    pattern, data = manager.detect_pattern("coarse", dataframes['df_univariate'])
    assert pattern == "univariate"
    assert data == {"column": "A"}

def test_detect_pattern_coarse_approach_monotone(dataframes, mock_dataframe_pattern_detector):
    mock_dataframe_pattern_detector.return_value.detect_pattern.return_value = ("monotone", {"matrix": "monotone_matrix"})
    manager = DatasetPatternManager()
    pattern, data = manager.detect_pattern("coarse", dataframes['df_monotone'])
    assert pattern == "monotone"
    assert data == {"matrix": "monotone_matrix"}

def test_detect_pattern_coarse_approach_non_monotone(dataframes, mock_dataframe_pattern_detector):
    mock_dataframe_pattern_detector.return_value.detect_pattern.return_value = ("non-monotone", {})
    manager = DatasetPatternManager()
    pattern, data = manager.detect_pattern("coarse", dataframes['df_non_monotone'])
    assert pattern == "non-monotone"
    assert data == {}

def test_detect_pattern_coarse_approach_no_missing_data(dataframes, mock_dataframe_pattern_detector):
    mock_dataframe_pattern_detector.return_value.detect_pattern.return_value = ("non-monotone", {})
    manager = DatasetPatternManager()
    pattern, data = manager.detect_pattern("coarse", dataframes['df_no_missing'])
    assert pattern == "non-monotone"
    assert data == {}

def test_detect_pattern_unsupported_approach(dataframes):
    manager = DatasetPatternManager()
    with pytest.raises(ValueError, match="Unsupported approach 'unsupported'. Supported approaches are: \['coarse'\]"):
        manager.detect_pattern("unsupported", dataframes['df_univariate'])

def test_detect_pattern_empty_dataframe(dataframes, mock_dataframe_pattern_detector):
    mock_dataframe_pattern_detector.return_value.detect_pattern.return_value = ("non-monotone", {})
    manager = DatasetPatternManager()
    pattern, data = manager.detect_pattern("coarse", dataframes['df_empty'])
    assert pattern == "non-monotone"
    assert data == {}
