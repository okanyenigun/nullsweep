import dask.dataframe as dd
import dask.array as da
from dask_ml.linear_model import LinearRegression
from sklearn.base import clone
from typing import Optional, Union, Iterable, Any
from .....bases.handler import AHandler


class RegressionImputerDask(AHandler):

    def __init__(
        self,
        column: Optional[Union[str, Iterable[str]]] = None,
        estimator: Any = None,
        predictor_strategy: str = "mean"
    ):
        self.column = column
        self.estimator = estimator or LinearRegression()
        self.predictor_strategy = predictor_strategy

    def fit(self, df: dd.DataFrame) -> "RegressionImputerDask":
        # Stateless: everything happens in fit_transform
        return self
    
    def transform(self, df: dd.DataFrame) -> dd.DataFrame:
        # Delegate to fit_transform for simplicity
        return self.fit_transform(df)
    
    def fit_transform(self, df: dd.DataFrame) -> dd.DataFrame:
        if self.column is None:
            null_mask = df.isnull().any().compute()
            targets = [col for col, has_null in null_mask.items() if has_null]
        elif isinstance(self.column, str):
            targets = [self.column]
        else:
            targets = list(self.column)

        result = df

        for target in targets:
            predictors = [c for c in result.columns if c != target]

            if self.predictor_strategy == "mean":
                fill_vals =  result[predictors].mean().compute().to_dict()
            elif self.predictor_strategy == "median":
                fill_vals = result[predictors].median().compute().to_dict()
            else:
                mode_df = result[predictors].map_partitions(lambda pdf: pdf.mode().iloc[0])
                fill_vals = mode_df.compute().to_dict()

            train = result[~result[target].isnull()]
            missing_mask = result[target].isnull()

            X_train = train[predictors].fillna(fill_vals)
            y_train = train[target]

            model = clone(self.estimator)
            model.fit(X_train.to_dask_array(lengths=True), y_train.to_dask_array(lengths=True))

            if missing_mask.any().compute():
                X_miss = result[predictors].fillna(fill_vals)[missing_mask]
                preds = model.predict(X_miss.to_dask_array(lengths=True))
                pred_series = dd.from_dask_array(preds, index=X_miss.index)

                result = result.assign(**{
                    target: result[target].mask(missing_mask, pred_series)
                }).persist()

        return result