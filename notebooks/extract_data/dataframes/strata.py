'''Functions to generate a dictionary of Dataframes splitted by strata (Estrato POF)
'''
from pandas import DataFrame
from copy import deepcopy
from .dictionaries.nutrients import get_right_nutrition

def split_into_stratas(df: DataFrame) -> dict:
    '''Split a Dataframe into a dictionary of dataframes. 
    Each key is a strata and each value is a dataframe with people in this strata
    
        Args:
            df (Dataframe): Dataframe with "ESTRATO_POF" into columns
            
        Retuns:
            dict (Dictionary): Dictionary witheach value is a dataframe with people in this strata
            
    '''
    stratas = df['ESTRATO_POF'].unique()
    splitted = dict()
    
    for strata in stratas:
        splitted[strata] = df[ df['ESTRATO_POF'] == strata ]
    
    return splitted