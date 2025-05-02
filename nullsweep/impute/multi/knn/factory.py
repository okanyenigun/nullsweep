from .pandas_engine.knn import KNNImputerWrapper


class KnnFactory:

    _handler_map = {
        "pandas": KNNImputerWrapper,
        "polars": KNNImputerWrapper,
        "dask": KNNImputerWrapper,
    }

    @staticmethod
    def get_handler(data_engine: str):
        if data_engine not in KnnFactory._handler_map:
            raise ValueError(f"Unsupported data engine. Choose from {list(KnnFactory._handler_map.keys())}. Sent: {data_engine}")
        
        return KnnFactory._handler_map[data_engine]

