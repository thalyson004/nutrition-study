from dataclasses import dataclass
from copy import deepcopy
from typing import Union

from app.components.extract_data.dataframes.dictionaries.nutrients import nutrients


@dataclass
class Nutrition:
    from .state import State

    def __init__(self, state: Union[State, any] = None):
        from .state import State
        from app.components.basic_dataframes import dictNutritionByMeal

        if isinstance(state, State):
            self.data = {key: 0 for key in nutrients.keys()}

            for code in state.keys():  # Meals code
                for nutrient in self.keys():  # Nutrient code
                    self.data[nutrient] += (
                        dictNutritionByMeal[code][nutrient] * state[code]
                    )
        elif type(state) is dict:
            self.data = state
        else:
            self.data = {key: 0 for key in nutrients.keys()}

    def keys(self):
        return list(self.data.keys())

    def values(self):
        return list(self.data.values())

    def change(self, nutritionCode: str, quantity: float):
        newState = deepcopy(self)
        newState[nutritionCode] += quantity
        return newState

    @staticmethod
    def keys() -> list:
        return list(nutrients.keys())

    @staticmethod
    def getDictNutrition(state: State) -> dict:
        """TODO: Describe the function"""
        return Nutrition(state).data

    @staticmethod
    def idealNutritionByEer(eer: float = None):
        """Given the EER factor, retuns a dictionary with the right nutrition

        Args:
            eer (float): EER factor

        Returns:
            nutrition dictionary (dict): Dictionary with the right nutrition of each nutrient for a specific person with EER factor

        """
        # TODO: Define the right quantities
        # FROM Eliseu 2020
        # Negative means lower than
        nutrients_quantiy = {
            "ENERGIA_KCAL": eer if eer != None else 50,
            "CHOTOT": eer * (55 / 100) if eer != None else 50,  # 55-75 eer
            "PTN": eer * (15 / 100) if eer != None else 50,  # 10-15 eer
            "LIP": (-1) * (-1) * (eer * (30 / 100) if eer != None else 50),  # 15–30 eer
            "FIBRA": 31,
            "COLEST": (-1) * (-1) * 300,
            "CALCIO": 868,
            # TODO: Use sodio as observed
            "SODIO": 0,
            "POTASSIO": 3510,
            "FERRO": 6.8,
            "MAGNESIO": 303,
            "TIAMINA": 0.9,
            "RIBOFLAVINA": 1,
            "NIACINA": 11.5,
            "PIRIDOXAMINA": 1.1,
            "COBALAMINA": 2,
            "VITC": 66.1,
            "VITA_RAE": 560,
            "COBRE": 0.7,
            "FOLATO": 322,
            "ZINCO": 8,
            "FOSFORO": 649,
        }

        return Nutrition(nutrients_quantiy)

    @staticmethod
    def idealNutritionByPersonId(personId: str = None):
        from app.components.basic_dataframes import dictPersonEer

        return Nutrition.idealNutritionByEer(dictPersonEer[personId])

    @staticmethod
    def directionDifference(initNutrition, targetNutrition):
        initNutrition: Nutrition = initNutrition
        targetNutrition: Nutrition = targetNutrition

        data = {
            key: targetNutrition[key] - initNutrition[key]
            for key in initNutrition.keys()
        }
        return Nutrition(data)

    @staticmethod
    def absDifference(initNutrition, targetNutrition, factor=1) -> float:
        initNutrition: Nutrition = initNutrition
        targetNutrition: Nutrition = targetNutrition

        return sum(
            [
                abs((initNutrition[key] * factor - targetNutrition[key]))
                for key in initNutrition.keys()
            ]
        )

    @staticmethod
    def absDifferenceNegativePenalty(
        initNutrition, targetNutrition, factor=1, mult=1.41
    ) -> float:
        initNutrition: Nutrition = initNutrition
        targetNutrition: Nutrition = targetNutrition

        return sum(
            [
                (
                    (initNutrition[key] * factor - targetNutrition[key])
                    if (initNutrition[key] * factor - targetNutrition[key]) > 0
                    else (initNutrition[key] * factor - targetNutrition[key]) * -mult
                )
                for key in initNutrition.keys()
            ]
        )

    @staticmethod
    def distanceDifference(initNutrition, targetNutrition, factor=1) -> float:
        initNutrition: Nutrition = initNutrition
        targetNutrition: Nutrition = targetNutrition

        return sum(
            [
                ((initNutrition[key] * factor - targetNutrition[key]))
                * ((initNutrition[key] * factor - targetNutrition[key]))
                for key in initNutrition.keys()
            ]
        )

    def distance() -> dict:
        return 0

    def __iter__(self):
        return iter(self.data)

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getitem__(self, index):
        return self.data[index]

    def __add__(self, temp):
        if self == None:
            return temp
        if temp == None:
            return self

        nutrition = Nutrition()
        for nutrient in nutrition.keys():
            nutrition[nutrient] = self[nutrient] + temp[nutrient]

        return nutrition

    def __truediv__(self, divValue):
        if isinstance(divValue, int) or isinstance(divValue, float):
            nutrition = Nutrition()
            for nutrientKey, nutrientValue in self.data.items():
                nutrition[nutrientKey] = nutrientValue / divValue
            return nutrition
        else:
            raise TypeError("Unsupported operand type(s)")

    def __str__(self):
        return f"Nutrition: {self.data}"
