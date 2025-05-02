import dask.dataframe as dd
import numpy as np
from typing import Optional, Union, Iterable, Any, Dict
from ....bases.handler import AHandler
from ....utils.structs import Structs
from .categorical import SingleCategoricalImputerDask
from .continuous import SimpleImputerDask
from .interpolate import LinearInterpolationImputerDask
from .direction import DirectionFillImputerDask
from ..pandas_engine.decision import SingleImputationStrategyDecider


class SingleImputationDask(AHandler):

    def __init__(self,
                 impute_strategy: str,
                 column: Optional[Union[Iterable[str], str]] = None,
                 strategy_decider: Any = SingleImputationStrategyDecider,
                 fill_value: Optional[Any] = None,
                 strategy_params: Optional[Dict[str, Any]] = None):
        self.impute_strategy = impute_strategy
        self.column = column
        self.fill_value = fill_value
        self.strategy_params = strategy_params or {}
        self.imputers: Dict[str, AHandler] = {}
        self._decider = strategy_decider()

        self._imputers_map = {
            "continuous": {
                "mean": SimpleImputerDask,
                "median": SimpleImputerDask,
                "most_frequent": SimpleImputerDask,
                "constant": SimpleImputerDask,
                "interpolate": LinearInterpolationImputerDask,
                "backfill": DirectionFillImputerDask,
                "forwardfill": DirectionFillImputerDask
            },
            "categorical": {
                "most_frequent": SingleCategoricalImputerDask,
                "constant": SingleCategoricalImputerDask,
                "least_frequent": SingleCategoricalImputerDask,
                "backfill": DirectionFillImputerDask,
                "forwardfill": DirectionFillImputerDask
            },
            "date": {
                "interpolate": LinearInterpolationImputerDask,
                "backfill": DirectionFillImputerDask,
                "forwardfill": DirectionFillImputerDask
            }
        }

    def fit(self, df: dd.DataFrame) -> "SingleImputationDask":

        if self.column is None:
            nulls = df.isnull().any().compute()
            columns = [col for col, has_null in nulls.items() if has_null]
        elif isinstance(self.column, str):
            columns = [self.column]
        else:
            columns = [col for col in self.column if col in df.columns]
        if not columns:
            raise ValueError("No columns to impute.")
        
        for col in columns:
            strategy = self.impute_strategy
            if strategy in (None, "auto"):
                sample = df[col].head(1000) 
                strategy = self._decider.decide_imputation_strategy(sample)

            dtype = df[col].dtype
            dtype_str = str(dtype).lower()

            if 'float' in dtype_str or 'int' in dtype_str:
                feature_type = "continuous"
            elif 'date' in dtype_str or 'datetime' in dtype_str:
                feature_type = "date"
            elif 'string' in dtype_str or 'object' in dtype_str:
                feature_type = "categorical"
            else:
                feature_type = "categorical"

            imputer_cls = self._imputers_map.get(feature_type, {}).get(strategy)
            if imputer_cls is None:
                raise ValueError(f"Strategy '{strategy}' not valid for feature type '{feature_type}'.")

            params = {"column": col}
            if self.fill_value is not None:
                params["fill_value"] = self.fill_value

            params.update(self.strategy_params)

            imputer = imputer_cls(**params)
            imputer.fit(df)
            self.imputers[col] = imputer

        return self

    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if not self.imputers:
            raise RuntimeError("SingleImputationDask not fitted: call 'fit' first.")
        
        result = df

        for _, imputer in self.imputers.items():
            result = imputer.transform(result)
        return result

    def fit_transform(self, df: dd.DataFrame) -> dd.DataFrame:
        return self.fit(df).transform(df)
