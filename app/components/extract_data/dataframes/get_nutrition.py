"""Functions to generate some Dataframes about nutritions of
the people.
"""

from pandas import DataFrame
from .dictionaries.nutrients import nutrients
from copy import deepcopy
from .dictionaries.nutrients import get_right_nutrition


def get_nutrients(df: DataFrame) -> DataFrame:
    """Extract dataframe with the sum of each nutrient by person

    Args:
        df (DataFrame): A dataframe with meals. Specify each nutrient in the columns.

    Returns:
         df (DataFrame): A dataframe with the sum of each nutrient by person
    """

    dfNutrition = df[["PESSOA"] + list(nutrients)]
    return dfNutrition.groupby("PESSOA", as_index=False).sum()


# TODO: This function is incomplete. Actually use only the EER factor.
def get_nutrients_dif(df: DataFrame) -> DataFrame:
    """Extract dataframe with the difference between the optinal nutrition and the current
    nutrition of each person.

    Actually:
    The dataframe must have the EER column.

    Optimal:
    The dataframe must have the columns:
        GENDER:str,
        AGE:float,
        HEIGHT:float,
        WEIGHT:float,
        ACTIVITY:str,

    Args:
        df (DataFrame): A dataframe with nutrients in columns

    Returns:
        df (DataFrame): A dataframe with the sum of each nutrient by person
    """
    df = df.copy()

    for nutrient in nutrients:
        df[nutrient + "_DIFF"] = df[nutrient] - get_right_nutrition(df["EER"])[nutrient]

    return df
