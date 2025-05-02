from .pandas_engine.manager import SingleImputationPandas
from .polars_engine.manager import SingleImputationPolars
from .dask_engine.manager import SingleImputationDask


class SimpleImputeFactory:

    _handler_map = {
        "pandas": SingleImputationPandas,
        "polars": SingleImputationPolars,
        "dask": SingleImputationDask
    }

    @staticmethod
    def get_handler(data_engine: str):
        if data_engine not in SimpleImputeFactory._handler_map:
            raise ValueError(f"Unsupported data engine. Choose from {list(SimpleImputeFactory._handler_map.keys())}. Sent: {data_engine}")
        
        return SimpleImputeFactory._handler_map[data_engine]

