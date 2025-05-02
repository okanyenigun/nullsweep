from .pandas_engine.indicator import MissingIndicatorPandas
from .polars_engine.indicator import MissingIndicatorPolars
from .dask_engine.indicator import MissingIndicatorDask


class MissingIndicatorFactory:

    _handler_map = {
        "pandas": MissingIndicatorPandas,
        "polars": MissingIndicatorPolars,
        "dask": MissingIndicatorDask,
    }

    @staticmethod
    def get_handler(data_engine: str):
        if data_engine not in MissingIndicatorFactory._handler_map:
            raise ValueError(f"Unsupported data engine. Choose from {list(MissingIndicatorFactory._handler_map.keys())}. Sent: {data_engine}")
        
        return MissingIndicatorFactory._handler_map[data_engine]