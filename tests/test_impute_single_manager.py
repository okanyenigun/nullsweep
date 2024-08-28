import pytest
import pandas as pd
from sklearn.impute import SimpleImputer
from nullsweep.impute.single.manager import SingleImputationManager  # Replace with correct import path
from nullsweep.impute.single.categorical import SingleCategoricalImputer
from nullsweep.impute.single.interpolate import LinearInterpolationImputer
from nullsweep.impute.single.direction import DirectionFillImputer
from nullsweep.impute.single.decision import SingleImputationStrategyDecider
from nullsweep.utils.structs import Structs


def test_impute_single_feature_continuous_mean():
    df = pd.DataFrame({'feature': [1, 2, None, 4, 5]})
    manager = SingleImputationManager()
    result_df = manager.impute_single_feature(df, 'feature', 'mean', None, None)
    expected_df = pd.DataFrame({'feature': [1, 2, 3, 4, 5]}, dtype=float)  # Match dtype to float64
    
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_impute_single_feature_continuous_median():
    df = pd.DataFrame({'feature': [1, 2, None, 4, 5, 100]})
    manager = SingleImputationManager()
    result_df = manager.impute_single_feature(df, 'feature', 'median', None, None)
    expected_df = pd.DataFrame({'feature': [1, 2, 4, 4, 5,  100]}, dtype=float)  # Match dtype to float64

    pd.testing.assert_frame_equal(result_df, expected_df)

def test_impute_single_feature_categorical_most_frequent():
    df = pd.DataFrame({'feature': ['a', 'b', None, 'a', 'b']})
    manager = SingleImputationManager()
    result_df = manager.impute_single_feature(df, 'feature', 'most_frequent', None, None)
    expected_df = pd.DataFrame({'feature': ['a', 'b', 'a', 'a', 'b']})

    pd.testing.assert_frame_equal(result_df, expected_df)

def test_impute_single_feature_with_auto_strategy():
    df = pd.DataFrame({'feature': [1, 2, None, 4, 5, 100]})
    manager = SingleImputationManager()
    result_df = manager.impute_single_feature(df, 'feature', 'auto', None, None)
    expected_df = pd.DataFrame({'feature': [1, 2, 3, 4, 5,  100]}, dtype=float)  # Match dtype to float64


    pd.testing.assert_frame_equal(result_df, expected_df)

def test_impute_single_feature_non_existent_feature():
    df = pd.DataFrame({'feature': [1, 2, 3]})
    manager = SingleImputationManager()

    with pytest.raises(ValueError, match="Feature 'non_existent' does not exist in the DataFrame."):
        manager.impute_single_feature(df, 'non_existent', 'mean', None, None)


def test_impute_single_feature_no_missing_values():
    df = pd.DataFrame({'feature': [1, 2, 3]})
    manager = SingleImputationManager()
    result_df = manager.impute_single_feature(df, 'feature', 'mean', None, None)
    expected_df = df.copy()  # No imputation should have been done

    pd.testing.assert_frame_equal(result_df, expected_df)


def test_impute_single_feature_with_fill_value():
    df = pd.DataFrame({'feature': [1, None, 3]})
    manager = SingleImputationManager()
    result_df = manager.impute_single_feature(df, 'feature', 'constant', 99, None)
    expected_df = pd.DataFrame({'feature': [1, 99, 3]}, dtype=float)  # Ensure dtype matches with float

    pd.testing.assert_frame_equal(result_df, expected_df)

def test_get_imputer_object_before_fit():
    manager = SingleImputationManager()
    with pytest.raises(ValueError, match="No imputer has been fitted yet."):
        manager.get_imputer_object()


def test_get_imputer_object_after_fit():
    df = pd.DataFrame({'feature': [1, 2, None, 4, 5]})
    manager = SingleImputationManager()
    manager.impute_single_feature(df, 'feature', 'mean', None, None)
    imputer = manager.get_imputer_object()

    assert isinstance(imputer, SimpleImputer)


def test_impute_single_feature_linear_interpolation():
    df = pd.DataFrame({'feature': [1, None, 3, None, 5]})
    manager = SingleImputationManager()
    result_df = manager.impute_single_feature(df, 'feature', 'interpolate', None, None)
    expected_df = pd.DataFrame({'feature': [1, 2, 3, 4, 5]}, dtype=float)  # Match dtype to float64

    pd.testing.assert_frame_equal(result_df, expected_df)
