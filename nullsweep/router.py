from typing import Any, Dict, Iterable, Optional, Union
from .deletion.factory import ColumnDeleterFactory
from .deletion.factory import ListWiseDeleterFactory
from .flag.factory import MissingIndicatorFactory
from .impute.multi.knn.factory import KnnFactory
from .impute.multi.mice.factory import MiceFactory
from .impute.multi.regression.factory import RegressionFactory
from .impute.single.factory import SimpleImputeFactory
from .bases.handler import AHandler
from .utils.structs import Structs


class ImputeFactory:

    def __init__(self):
        self._methods = {
            "delete_column": ColumnDeleterFactory,
            "listwise": ListWiseDeleterFactory,
            "flag": MissingIndicatorFactory,
            "knn": KnnFactory,
            "mice": MiceFactory,
            "regression": RegressionFactory,
            "mean": SimpleImputeFactory,
            "median": SimpleImputeFactory,
            "most_frequent": SimpleImputeFactory,
            "constant": SimpleImputeFactory,
            "interpolate": SimpleImputeFactory,
            "backfill": SimpleImputeFactory,
            "forwardfill": SimpleImputeFactory,
            "auto": SimpleImputeFactory,
        }

    def create_imputer(
            self, 
            strategy: str, 
            data_engine: str,
            column: Optional[Union[Iterable, str]], 
            fill_value: Optional[Any], 
            strategy_params: Optional[Dict[str, Any]],
            **kwargs
            ) -> AHandler:
        
        operator_factory = self._methods.get(strategy)
        if operator_factory is None:
            raise RuntimeError(f"Unsupported strategy '{strategy}'." 
                               f"Supported strategies are: {list(self._methods.keys())}")

        operator_class = operator_factory.get_handler(data_engine)

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

