"""Functions to generate some Dataframes meals consumed by each person
"""
from pandas import DataFrame
from .dictionaries.nutrients import nutrients
from copy import deepcopy
from .dictionaries.nutrients import get_right_nutrition
