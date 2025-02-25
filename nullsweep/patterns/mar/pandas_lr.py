import pandas as pd
from typing import Dict, Tuple
from .base import MarTypeLogisticDetector


class MarLRPandas(MarTypeLogisticDetector):

    def detect_pattern(self) -> Tuple[bool, Dict[str, bool]]:
        missing_encoded_values = self.df[self.feature].isna().astype(int)
        candidate_feature_list = [col for col in self.df.columns if col != self.feature]

        for candidate in candidate_feature_list:
            if not pd.api.types.is_numeric_dtype(self.df[candidate]):
                continue

            self._check_candidate(missing_encoded_values, candidate)
        
        return self._mar, self._mappings
    
    def _check_candidate(self, missing_encoded_values: pd.Series, candidate: str) -> None:
        cleaned_target_values, df_candidate = self._clean_data(missing_encoded_values, candidate)

        if cleaned_target_values.empty or df_candidate.empty:
            raise ValueError(f"The candidate feature '{candidate}' contains no valid numeric values." 
                             f"Ensure the candidate feature has numeric values and no missing data.")
        
        model_result = self._fit_logistic(cleaned_target_values, df_candidate)

        self._mappings[candidate] = self._evaluate_mar(model_result, candidate)
        
        if self._mappings[candidate]:
            self._mar = True
        
        return
    
    def _clean_data(self, missing_encoded_values: pd.Series, candidate: str) -> Tuple[pd.Series, pd.DataFrame]:
        candidate_missing_indexes = self.df[self.df[candidate].isna()].index

        cleaned_candidate_values = self.df[candidate].drop(candidate_missing_indexes)
        cleaned_target_values = missing_encoded_values.drop(candidate_missing_indexes)

        if cleaned_target_values.empty or cleaned_candidate_values.empty:
            return pd.Series(), pd.DataFrame()
        
        cleaned_target_values.reset_index(drop=True, inplace=True)
        cleaned_candidate_values.reset_index(drop=True, inplace=True)
        
        df_candidate = cleaned_candidate_values.to_frame()
        df_candidate['new_column'] = 1
        
        return cleaned_target_values, df_candidate