from .pandas_engine.regression import RegressionImputer


class RegressionFactory:

    _handler_map = {
        "pandas": RegressionImputer,
        "polars": RegressionImputer,
    }

    @staticmethod
    def get_handler(data_engine: str):
        if data_engine not in RegressionFactory._handler_map:
            raise ValueError(f"Unsupported data engine. Choose from {list(RegressionFactory._handler_map.keys())}. Sent: {data_engine}")
        
        return RegressionFactory._handler_map[data_engine]

