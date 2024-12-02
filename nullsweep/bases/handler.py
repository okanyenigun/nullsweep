import pandas as pd
from abc import ABC, abstractmethod


class AHandler(ABC):

    @abstractmethod
    def fit(self, df: pd.DataFrame):
        """
        Fit the handler to the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to fit the handler to.
        """
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to transform.

        Returns:
            pd.DataFrame: The transformed DataFrame.
        """

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and transform the DataFrame.
        """
        self.fit(df)
        return self.transform(df)
