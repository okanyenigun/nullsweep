import numpy as np
import pandas as pd
import dask.dataframe as dd
from typing import Dict, Tuple
from .base import MarTypeLogisticDetector


class MarLRDask(MarTypeLogisticDetector):
    
    def detect_pattern(self) -> Tuple[bool, Dict[str, bool]]:
        missing_encoded_values = self.df[self.feature].isnull().astype(int)
        candidate_features = [col for col in self.df.columns if col != self.feature]

        for candidate in candidate_features:
            if not np.issubdtype(self.df[candidate].dtype, np.number):
                continue
            self._check_candidate(missing_encoded_values, candidate)
        
        return self._mar, self._mappings
    
    def _check_candidate(self, missing_encoded_values: dd.Series, candidate: str) -> None:
        cleaned_target, cleaned_candidate = self._clean_data(missing_encoded_values, candidate)

        if cleaned_target.empty or cleaned_candidate.empty:
            raise ValueError(f"The candidate feature '{candidate}' contains no valid numeric values." 
                             f"Ensure the candidate feature has numeric values and no missing data.")
        
        model_result = self._fit_logistic(cleaned_target, cleaned_candidate)
        mar_status = self._evaluate_mar(model_result, candidate)

        self._mappings[candidate] = mar_status

        if mar_status:
            self._mar = True
        return
    
    def _clean_data(self, missing_encoded_values: dd.Series, candidate: str) -> Tuple[dd.Series, dd.DataFrame]:
        temp_ddf = self.df[[candidate]].assign(missing=missing_encoded_values)  
        temp_ddf_clean = temp_ddf.dropna(subset=[candidate])
        temp_pdf = temp_ddf_clean.compute()

        if temp_pdf.empty:
            return pd.Series(), pd.DataFrame()
        
        target_clean = temp_pdf["missing"].astype(int)
        features_clean = temp_pdf[[candidate]].assign(new_column=1)

        return target_clean, features_clean