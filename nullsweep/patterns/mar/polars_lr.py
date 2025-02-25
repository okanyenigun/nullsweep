import polars as pl
from typing import Dict, Tuple
from .base import MarTypeLogisticDetector


class MarLRPolars(MarTypeLogisticDetector):

    def detect_pattern(self) -> Tuple[bool, Dict[str, bool]]:
        missing_encoded_values = self.df[self.feature].is_null().cast(pl.Int32)
        candidate_feature_list = [col for col in self.df.columns if col != self.feature]

        for candidate in candidate_feature_list:
            if not self.df.schema[candidate] in [pl.Float32, pl.Float64, pl.Int32, pl.Int64, pl.UInt32, pl.UInt64]:
                continue

            self._check_candidate(missing_encoded_values, candidate)

        return self._mar, self._mappings
    
    def _check_candidate(self, missing_encoded_values: pl.Series, candidate: str) -> None:
        cleaned_target_values, df_candidate = self._clean_data(missing_encoded_values, candidate)

        if cleaned_target_values.is_empty() or df_candidate.is_empty():
            raise ValueError(f"The candidate feature '{candidate}' contains no valid numeric values." 
                             f"Ensure the candidate feature has numeric values and no missing data.")
        
        model_result = self._fit_logistic(cleaned_target_values.to_pandas(), df_candidate.to_pandas())

        self._mappings[candidate] = self._evaluate_mar(model_result, candidate)
        
        if self._mappings[candidate]:
            self._mar = True
        return
    
    def _clean_data(self, missing_encoded_values: pl.Series, candidate: str) -> Tuple[pl.Series, pl.DataFrame]:
        mask = self.df[candidate].is_not_null()
        
        cleaned_candidate_values = self.df.filter(mask).select(candidate)
        cleaned_target_values = missing_encoded_values.filter(mask)

        if cleaned_target_values.is_empty() or cleaned_candidate_values.is_empty():
            return pl.Series(), pl.DataFrame()

        df_candidate = cleaned_candidate_values.with_columns(pl.lit(1).alias("new_column"))

        return cleaned_target_values, df_candidate
    