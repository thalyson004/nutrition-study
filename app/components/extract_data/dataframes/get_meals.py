"""Functions to generate some Dataframes meals consumed by each person
"""
from pandas import DataFrame
from .dictionaries.nutrients import nutrients
from copy import deepcopy
from .dictionaries.nutrients import get_right_nutrition


def get_meal_state(df: DataFrame) -> DataFrame:
    """Extract dataframe with the sum of each nutrient by person

    Args:
        df (DataFrame): A dfConsumo dataframe

    Returns:
         df (DataFrame): A dataframe initial state of each person
    """

    dfState = DataFrame(df["PESSOA"].unique(), columns=["PESSOA"])

    countQuantity = {}

    mealsCodes = get_meals_codes_list(df)

    for index, row in df.iterrows():
        try:
            countQuantity[(row["PESSOA"], row["COD_TBCA"])] += 0
        except:
            countQuantity[(row["PESSOA"], row["COD_TBCA"])] = 0

        countQuantity[(row["PESSOA"], row["COD_TBCA"])] += row["QTD"]

    def get_QTD(pessoa: str, tbca: str) -> int:
        try:
            return countQuantity[(pessoa, tbca)]
        except:
            return 0

    for code in mealsCodes:
        dfState[code] = dfState["PESSOA"].apply(lambda pessoa: get_QTD(pessoa, code))

    return dfState


def get_meals_codes(df: DataFrame) -> DataFrame:
    """Extract dataframe all meals

    Args:
        df (DataFrame): A dataframe with COD_TBCA columns

    Returns:
        df (DataFrame): A dataframe with all uniques COD_TBCA codes
    """

    return DataFrame(df["COD_TBCA"].unique(), columns=["COD_TBCA"])


def get_meals_codes_list(df: DataFrame) -> list:
    """Extract dataframe all meals

    Args:
        df (DataFrame): A dataframe with COD_TBCA columns

    Returns:
        l (list): A array list with all uniques COD_TBCA codes
    """

    return DataFrame(df["COD_TBCA"].unique(), columns=["COD_TBCA"])[
        "COD_TBCA"
    ].to_list()
