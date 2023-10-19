from dataclasses import dataclass
from typing import Union

from app.components.extract_data.dataframes.dictionaries.nutrients import nutrients


@dataclass
class Nutrition:
    from .state import State

    data: dict = None

    def __getitem__(self, index):
        return self.data[index]

    def keys(self):
        return self.data.keys()

    def __init__(self, state: Union[State, any]):
        from .state import State
        from app.components.basic_dataframes import dictNutritionByMeal

        if type(state) is State:
            self.data = {key: 0 for key in nutrients.keys()}

            for code in state.keys():  # Meals code
                for nutrient in self.keys():  # Nutrient code
                    self.data[nutrient] += (
                        dictNutritionByMeal[code][nutrient] * state[code]
                    )
        else:
            self.data = {key: 0 for key in nutrients.keys()}

    @staticmethod
    def getDictNutrition(state: State) -> dict:
        return Nutrition(state).data

    # def __setitem__(self, index, value):
    #     self.data[index] = value
