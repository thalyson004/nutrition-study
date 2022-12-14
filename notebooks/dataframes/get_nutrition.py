from pandas import DataFrame
from dictionaries.nutrients import nutrients
from copy import deepcopy
from dictionaries.nutrients import get_right_nutrition
 
def get_nutrients(df: DataFrame) -> DataFrame:
    '''
        Input: A dataframe with nutrients in columns
        Output: A dataframe with the sum of each nutrient by person
    '''
    
    dfNutrition = df[ ['PESSOA'] + list(nutrients.keys()) ]
    return dfNutrition.groupby("PESSOA", as_index=False).sum()

# TODO: Finish this function
def get_nutrients_dif(df: DataFrame) -> DataFrame:
    '''
        The dateframe must have columns:
            GENDER:str,
            AGE:float,
            HEIGHT:float,
            WEIGHT:float,
            ACTIVITY:str,
        Input: A dataframe with nutrients in columns
        Output: A dataframe with the sum of each nutrient by person
    '''
    df = df.copy()
    
    for nutrient in nutrients:
        df[nutrient+'_DIFF'] = df[nutrient]-get_right_nutrition(df['EER'])[nutrient]
    
    return df