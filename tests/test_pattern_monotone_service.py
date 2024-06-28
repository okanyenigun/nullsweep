import pytest
import pandas as pd
from nullsweep.patterns.monotone.service import DataFramePatternDetector
from nullsweep.utils.dummies import Dummy

@pytest.fixture
def dataframes():
    # Define various dataframes for testing
    df_univariate = Dummy.get_univariate_df()
    df_monotone = Dummy.get_monotone_df()
    df_non_monotone = Dummy.get_non_monotone()
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

def test_detect_pattern_univariate_missing(dataframes):
    detector = DataFramePatternDetector(dataframes['df_univariate'])
    assert detector.detect_pattern() == ("univariate", {"column": "C"})

def test_detect_pattern_monotone_missing(dataframes):
    detector = DataFramePatternDetector(dataframes['df_monotone'])
    pattern, details = detector.detect_pattern()
    assert pattern == "monotone"
    assert isinstance(details["matrix"], pd.DataFrame)
    assert details["matrix"].any().any() == True

def test_detect_pattern_non_monotone_missing(dataframes):
    detector = DataFramePatternDetector(dataframes['df_non_monotone'])
    assert detector.detect_pattern() == ("non-monotone", {})

def test_detect_pattern_no_missing_data(dataframes):
    detector = DataFramePatternDetector(dataframes['df_no_missing'])
    assert detector.detect_pattern() == ("non-monotone", {})

# Unit tests for detect_univariate
def test_detect_univariate_single_column_missing(dataframes):
    detector = DataFramePatternDetector(dataframes['df_univariate'])
    assert detector.detect_univariate() == "C"

def test_detect_univariate_multiple_columns_missing(dataframes):
    detector = DataFramePatternDetector(dataframes['df_monotone'])
    assert detector.detect_univariate() is None

def test_detect_univariate_no_missing_data(dataframes):
    detector = DataFramePatternDetector(dataframes['df_no_missing'])
    assert detector.detect_univariate() is None

def test_detect_univariate_all_columns_missing(dataframes):
    df_all_missing = pd.DataFrame({
        'A': [None, None, None],
        'B': [None, None, None]
    })
    detector = DataFramePatternDetector(df_all_missing)
    assert detector.detect_univariate() is None

# Unit tests for detect_monotone
def test_detect_monotone_single_column_missing(dataframes):
    df_single_missing = pd.DataFrame({
        'A': [1, 2, None, 4],
        'B': [5, 6, 7, 8]
    })
    detector = DataFramePatternDetector(df_single_missing)
    flag, _ = detector.detect_monotone()
    assert flag == False

def test_detect_monotone_no_missing_data(dataframes):
    detector = DataFramePatternDetector(dataframes['df_no_missing'])
    flag, _ = detector.detect_monotone()
    assert flag == False

def test_detect_monotone_complete_monotone_pattern(dataframes):
    detector = DataFramePatternDetector(dataframes['df_monotone'])
    monotone, matrix = detector.detect_monotone()
    assert monotone == True
    assert matrix.any().any() == True

def test_detect_monotone_partial_monotone_pattern(dataframes):
    df_partial_monotone = pd.DataFrame({
        'A': [None, 2, None, 4],
        'B': [1, None, None, 4],
        'C': [None, 2, 3, None]
    })
    detector = DataFramePatternDetector(df_partial_monotone)
    monotone, matrix = detector.detect_monotone()
    assert monotone == False
    assert matrix.any().any() == False

def test_detect_monotone_non_monotone_pattern(dataframes):
    detector = DataFramePatternDetector(dataframes['df_non_monotone'])
    monotone, matrix = detector.detect_monotone()
    assert monotone == False
    assert matrix.any().any() == False

def test_detect_monotone_empty_dataframe(dataframes):
    detector = DataFramePatternDetector(dataframes['df_empty'])
    monotone, matrix = detector.detect_monotone()
    assert monotone == False
    assert matrix.empty == True
