"""Functions to generate some Dataframes meals consumed by each person
"""
from pandas import DataFrame
from .dictionaries.nutrients import nutrients
from copy import deepcopy
from .dictionaries.nutrients import get_right_nutrition


# TODO: implement
def get_meal_state(df: DataFrame) -> DataFrame:
    """Extract dataframe with the sum of each nutrient by person

    Args:
        df (DataFrame): A dataframe with meals. Specify each nutrient in the columns.

    Returns:
         df (DataFrame): A dataframe with the sum of each nutrient by person
    """

    dfNutrition = df[["PESSOA"] + list(nutrients.keys())]
    return dfNutrition.groupby("PESSOA", as_index=False).sum()


# Implement
def get_meals_codes(df: DataFrame) -> DataFrame:
    """Extract dataframe all meals

    Args:
        df (DataFrame): A dataframe with COD_TBCA columns

    Returns:
        df (DataFrame): A dataframe with all uniques COD_TBCA codes
    """

    return DataFrame(df["COD_TBCA"].unique(), columns=["COD_TBCA"])
