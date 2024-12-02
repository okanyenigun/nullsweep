from typing import Any, Dict, Iterable, Optional, Union
from .deletion.column import ColumnDeleter
from .deletion.listwise import ListWiseDeleter
from .flag.indicator import MissingIndicator
from .impute.multi.knn import KNNImputerWrapper
from .impute.multi.mice import MICEImputer
from .impute.multi.regression import RegressionImputer
from .impute.single.manager import SingleImputationWrapper
from .bases.handler import AHandler
from .utils.structs import Structs


class HandlingRouter:

    def __init__(self):
        self._methods = {
            "delete_column": ColumnDeleter,
            "listwise":ListWiseDeleter,
            "flag": MissingIndicator,
            "knn": KNNImputerWrapper,
            "mice": MICEImputer,
            "regression": RegressionImputer,
            "mean": SingleImputationWrapper,
            "median":SingleImputationWrapper,
            "most_frequent":SingleImputationWrapper,
            "least_frequent":SingleImputationWrapper,
            "constant":SingleImputationWrapper,
            "interpolate": SingleImputationWrapper,
            "backfill": SingleImputationWrapper,
            "forwardfill": SingleImputationWrapper,
            "auto": SingleImputationWrapper,
        }

    def route(self, 
              strategy: str, 
              column: Optional[Union[Iterable, str]], 
              fill_value: Optional[Any], 
              strategy_params: Optional[Dict[str, Any]], 
              **kwargs
              ) -> AHandler:
        
        operator_class = self._methods.get(strategy)

        if operator_class is None:
            raise ValueError(f"Strategy {strategy} not found. Available strategies are: {list(self._methods.keys())}")
        
        params = {
            "impute_strategy": strategy,
            "column": column,
            "fill_value": fill_value,
            "strategy_params": strategy_params
        }

        params.update(kwargs)

        atts = Structs.filter_kwargs_for_class(operator_class, params)

        operator = operator_class(**atts)

        return operator