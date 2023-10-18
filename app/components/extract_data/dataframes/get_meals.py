"""Functions to generate some Dataframes meals consumed by each person
"""
from pandas import DataFrame
from .dictionaries.nutrients import nutrients
from copy import deepcopy
from .dictionaries.nutrients import get_right_nutrition


def get_meals_codes(df: DataFrame) -> DataFrame:
    """Extract dataframe all meals

    Args:
        df (DataFrame): A dataframe with COD_TBCA columns

    Returns:
        df (DataFrame): A dataframe with all uniques COD_TBCA codes
    """

    return DataFrame(df["COD_TBCA"].unique(), columns=["COD_TBCA"])


def get_meals_codes_list(df: DataFrame) -> list:
    """Extract a list of unique COD_TBCA from dataframe

    Args:
        df (DataFrame): A dataframe with COD_TBCA columns

    Returns:
        l (list): A array list with all uniques COD_TBCA codes
    """

    return DataFrame(df["COD_TBCA"].unique(), columns=["COD_TBCA"])[
        "COD_TBCA"
    ].to_list()
