from .pandas_engine.column import ColumnDeleterPandas
from .pandas_engine.listwise import ListWiseDeleterPandas
from .polars_engine.column import ColumnDeleterPolars
from .polars_engine.listwise import ListWiseDeleterPolars
from .dask_engine.column import ColumnDeleterDask
from .dask_engine.listwise import ListWiseDeleterDask
from ..bases.handler import AHandler


class ColumnDeleterFactory:

    _handler_map = {
        "pandas": ColumnDeleterPandas,
        "polars": ColumnDeleterPolars,
        "dask": ColumnDeleterDask,
    }

    @staticmethod
    def get_handler(data_engine: str) -> AHandler:
        if data_engine not in ColumnDeleterFactory._handler_map:
            raise ValueError(f"Unsupported data engine. Choose from {list(ColumnDeleterFactory._handler_map.keys())}. Sent: {data_engine}")
        
        return ColumnDeleterFactory._handler_map[data_engine]
    

class ListWiseDeleterFactory:

    _handler_map = {
        "pandas": ListWiseDeleterPandas,
        "polars": ListWiseDeleterPolars,
        "dask": ListWiseDeleterDask,
    }

    @staticmethod
    def get_handler(data_engine: str) -> AHandler:
        if data_engine not in ListWiseDeleterFactory._handler_map:
            raise ValueError(f"Unsupported data engine. Choose from {list(ListWiseDeleterFactory._handler_map.keys())}. Sent: {data_engine}")
        
        return ListWiseDeleterFactory._handler_map[data_engine]

