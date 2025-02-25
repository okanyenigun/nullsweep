import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import L1BinaryResultsWrapper
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Any
from ...config import DataType


class MarTypeLogisticDetector(ABC):
    """
    A class to detect Missing At Random (MAR) patterns using logistic regression.
    
    Attributes:
        df (DataType): The DataFrame containing the data.
        feature (str): The feature/column to check for missing data patterns.
        p_value_threshold (float): The threshold for p-values to consider a predictor significant.
        pseudo_r_squared_threshold (float): The threshold for pseudo R-squared to consider the model fit significant.
    """
    def __init__(self, df: DataType, feature: str, p_value_threshold: float=0.05, pseudo_r_squared_threshold: float=0.2):
        self.df = df
        self.feature = feature
        self._mar = False
        self._mappings = {}
        self.p_value_threshold = p_value_threshold
        self.pseudo_r_squared_threshold = pseudo_r_squared_threshold

    @abstractmethod
    def detect_pattern(self) -> Tuple[bool, Dict[str, bool]]:
        """
        Detects if the missing data pattern in the specified feature is MAR.
        
        Returns:
            Tuple[bool, Dict[str, bool]]: A tuple containing a boolean indicating if any MAR pattern is detected
                                           and a dictionary with candidate features and their MAR status.
        """
        pass

    def _check_candidate(self, missing_encoded_values: Any, candidate: str) -> None:
        """
        Checks if the candidate feature indicates an MAR pattern and updates the mappings.
        
        Args:
            missing_encoded_values (Any): A series indicating missing values in the target feature.
            candidate (str): The candidate feature to check.
        """
        pass


    def _clean_data(self, missing_encoded_values: Any, candidate: str) -> Tuple[Any, DataType]:
        """
        Cleans the data by removing rows with missing values in the candidate feature.
        
        Args:
            missing_encoded_values (Any): A series indicating missing values in the target feature.
            candidate (str): The candidate feature to clean.
        
        Returns:
            Tuple[Any, DataType]: The cleaned target values and candidate DataFrame.
        """
        pass

    def _fit_logistic(self, cleaned_target_values: pd.Series, df_candidate: str) -> L1BinaryResultsWrapper:
        """
        Fits a logistic regression model to the cleaned data.
        
        Args:
            cleaned_target_values (pd.Series): The cleaned target values.
            df_candidate (pd.DataFrame): The cleaned candidate DataFrame.
        
        Returns:
            L1BinaryResultsWrapper: The fitted logistic regression model results.
        """
        try:
            logit_model = sm.Logit(cleaned_target_values, df_candidate)
            result = logit_model.fit_regularized(method='l1', alpha=1.0, disp=False)
            return result
        except Exception as e:
            raise ValueError(f"Logistic regression model fitting failed. Ensure the data is appropriate for logistic regression. Error details: {e}")
    
    def _evaluate_mar(self, model_result: L1BinaryResultsWrapper, candidate: str) -> bool:
        """
        Evaluates if the model results indicate an MAR pattern for the candidate feature.
        
        Args:
            model_result (L1BinaryResultsWrapper): The results of the fitted logistic regression model.
            candidate (str): The candidate feature being evaluated.
        
        Returns:
            bool: True if MAR pattern is detected, False otherwise.
        """
        return (self._is_predictor_significant(model_result, candidate) and 
                self._is_model_fit_significant(model_result) and 
                self._is_lrt_significant(model_result))

    def _is_predictor_significant(self, model_result: L1BinaryResultsWrapper, candidate: str) -> bool:
        """
        Checks if the predictor's p-value is significant.
        
        Args:
            model_result (L1BinaryResultsWrapper): The results of the fitted logistic regression model.
            candidate (str): The candidate feature being evaluated.
        
        Returns:
            bool: True if the predictor is significant, False otherwise.
        """
        return model_result.pvalues[candidate] < self.p_value_threshold
    
    def _is_model_fit_significant(self, model_result: L1BinaryResultsWrapper) -> bool:
        """
        Checks if the model's pseudo R-squared is significant.
        
        Args:
            model_result (L1BinaryResultsWrapper): The results of the fitted logistic regression model.
        
        Returns:
            bool: True if the model fit is significant, False otherwise.
        """
        return model_result.prsquared > self.pseudo_r_squared_threshold
    
    def _is_lrt_significant(self, model_result: L1BinaryResultsWrapper) -> bool:
        """
        Checks if the model's log-likelihood ratio test (LRT) is significant.
        
        Args:
            model_result (L1BinaryResultsWrapper): The results of the fitted logistic regression model.
        
        Returns:
            bool: True if the LRT is significant, False otherwise.
        """
        return model_result.llr_pvalue < self.p_value_threshold