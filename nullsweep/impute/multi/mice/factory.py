from .pandas_engine.mice import MICEImputer


class MiceFactory:

    _handler_map = {
        "pandas": MICEImputer,
        "polars": MICEImputer,
        "dask": MICEImputer,
    }

    @staticmethod
    def get_handler(data_engine: str):
        if data_engine not in MiceFactory._handler_map:
            raise ValueError(f"Unsupported data engine. Choose from {list(MiceFactory._handler_map.keys())}. Sent: {data_engine}")
        
        return MiceFactory._handler_map[data_engine]

